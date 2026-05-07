# src/agents/sistema_phi3_db.py
"""
Sistema Multiagente Médico con LangGraph v3.0
- Procesamiento paralelo: Diagnóstico ∥ Tratamiento (ThreadPoolExecutor)
- Rutas condicionales: EMERGENCIA / LEVE / MODERADO-GRAVE
- Caché en dos niveles (agente + consulta completa)
- Persistencia en SQLite
"""

import time
import sys
import os
import concurrent.futures
import sqlite3
from typing import Optional, TypedDict

import requests
from langgraph.graph import StateGraph, END

# Rutas de importación
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from cache.cache_manager import cache_manager
from utils.logger import logger
from agents.prompts import (
    prompt_triage,
    prompt_diagnostico,
    prompt_tratamiento,
    prompt_emergencia,
    prompt_autocuidado,
    parsear_nivel_urgencia,
)

MODELO = settings.DEFAULT_MODEL


# ============================================================
# ESTADO DEL GRAFO
# ============================================================

class EstadoMedico(TypedDict):
    consulta: str
    paciente_id: int
    edad: int
    nombre: str
    triage: str
    diagnostico: str
    tratamiento: str
    nivel_urgencia: str
    tiempo_procesamiento: float
    from_cache: bool
    protocolo: str  # "normal" | "emergencia" | "leve"


# ============================================================
# BASE DE DATOS
# ============================================================

class DatabaseManager:
    """Gestor de base de datos SQLite para el historial clínico."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS pacientes (
                    id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre   TEXT,
                    edad     INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS consultas (
                    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                    paciente_id         INTEGER,
                    sintomas            TEXT,
                    triage              TEXT,
                    diagnostico         TEXT,
                    tratamiento         TEXT,
                    nivel_urgencia      TEXT,
                    protocolo           TEXT DEFAULT 'normal',
                    tiempo_procesamiento REAL,
                    modelo_ia           TEXT,
                    from_cache          BOOLEAN DEFAULT FALSE,
                    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
                );
            """)

    def crear_paciente(self, nombre: str = None, edad: int = 0) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "INSERT INTO pacientes (nombre, edad) VALUES (?, ?)", (nombre, edad)
            )
            return cur.lastrowid

    def guardar_consulta(self, datos: dict) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                """INSERT INTO consultas
                   (paciente_id, sintomas, triage, diagnostico, tratamiento,
                    nivel_urgencia, protocolo, tiempo_procesamiento, modelo_ia, from_cache)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (
                    datos.get("paciente_id"),
                    datos.get("sintomas"),
                    datos.get("triage"),
                    datos.get("diagnostico"),
                    datos.get("tratamiento"),
                    datos.get("nivel_urgencia"),
                    datos.get("protocolo", "normal"),
                    datos.get("tiempo_procesamiento"),
                    datos.get("modelo_ia"),
                    datos.get("from_cache", False),
                ),
            )
            return cur.lastrowid

    def obtener_consultas(self, limite: int = 10) -> list:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(
                """SELECT c.*, p.nombre, p.edad
                   FROM consultas c
                   LEFT JOIN pacientes p ON c.paciente_id = p.id
                   ORDER BY c.created_at DESC LIMIT ?""",
                (limite,),
            )
            return [dict(r) for r in cur.fetchall()]

    def close(self):
        pass  # sqlite3 cierra la conexión automáticamente por contexto


# Instancia global de BD
db = DatabaseManager(settings.DATABASE_PATH)


# ============================================================
# FUNCIÓN OLLAMA
# ============================================================

def consultar_ollama(prompt: str, contexto: str = "") -> tuple:
    """Consulta al modelo Ollama con timeout y manejo de errores."""
    inicio = time.time()
    try:
        resp = requests.post(
            settings.OLLAMA_URL,
            json={
                "model": MODELO,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": settings.MAX_TOKENS,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1,
                },
            },
            timeout=settings.MODEL_TIMEOUT,
        )
        if resp.status_code == 200:
            return resp.json().get("response", "").strip(), time.time() - inicio
        return f"Error HTTP {resp.status_code}", 0
    except requests.exceptions.Timeout:
        return "Error: Timeout — Ollama tardó demasiado", 0
    except Exception as e:
        return f"Error: {str(e)[:80]}", 0


# ============================================================
# AGENTES
# ============================================================

def agente_triage(state: EstadoMedico) -> dict:
    """Agente de triage con caché y prompts estructurados."""
    print("   🟡 [1/3] TRIAGE...", end=" ", flush=True)

    cache_key = f"triage_{state['consulta'].lower().strip()}_{state.get('edad', 0)}"
    cached = cache_manager.get(cache_key)

    if cached:
        print("✓ (desde caché)")
        return {
            "triage": cached["triage"],
            "nivel_urgencia": cached["nivel_urgencia"],
            "from_cache": True,
        }

    prompt = prompt_triage(state["consulta"], state.get("edad"), state.get("nombre"))
    respuesta, tiempo = consultar_ollama(prompt, "triage")
    nivel = parsear_nivel_urgencia(respuesta)

    cache_manager.set(cache_key, {"triage": respuesta, "nivel_urgencia": nivel})
    print(f"✓ ({tiempo:.1f}s) → {nivel}")
    logger.info(f"Triage: {nivel} — {respuesta[:60]}")

    return {"triage": respuesta, "nivel_urgencia": nivel}


# --- Funciones internas para ejecución paralela ---

def _run_diagnostico(state: EstadoMedico) -> str:
    prompt = prompt_diagnostico(state["consulta"], state.get("edad"))
    respuesta, tiempo = consultar_ollama(prompt, "diagnostico")
    print(f"      ├─ 🔵 Diagnóstico ✓ ({tiempo:.1f}s)")
    logger.info(f"Diagnóstico completado en {tiempo:.1f}s")
    return respuesta


def _run_tratamiento(state: EstadoMedico) -> str:
    prompt = prompt_tratamiento(
        state["consulta"], state.get("nivel_urgencia", "MODERADO"), state.get("edad")
    )
    respuesta, tiempo = consultar_ollama(prompt, "tratamiento")
    print(f"      └─ 🟢 Tratamiento ✓ ({tiempo:.1f}s)")
    logger.info(f"Tratamiento completado en {tiempo:.1f}s")
    return respuesta


def agente_paralelo(state: EstadoMedico) -> dict:
    """Ejecuta diagnóstico Y tratamiento en paralelo con ThreadPoolExecutor."""
    print("   ⚡ [2-3/3] DIAGNÓSTICO ∥ TRATAMIENTO (paralelo)...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        fut_diag = executor.submit(_run_diagnostico, state)
        fut_trat = executor.submit(_run_tratamiento, state)
        diagnostico = fut_diag.result()
        tratamiento = fut_trat.result()

    return {"diagnostico": diagnostico, "tratamiento": tratamiento, "protocolo": "normal"}


def agente_protocolo_emergencia(state: EstadoMedico) -> dict:
    """Protocolo de emergencia: respuesta inmediata sin esperar ciclo completo de LLM."""
    print("   🚨 EMERGENCIA MÉDICA DETECTADA — Protocolo urgente activado")
    logger.warning(f"EMERGENCIA detectada: {state['consulta'][:100]}")

    return {
        "diagnostico": "⚠️ EMERGENCIA — Se requiere atención médica inmediata.",
        "tratamiento": prompt_emergencia(state["consulta"]),
        "protocolo": "emergencia",
    }


def agente_protocolo_leve(state: EstadoMedico) -> dict:
    """Protocolo leve: orientación domiciliaria sin diagnóstico diferencial completo."""
    print("   💚 [2/2] PROTOCOLO LEVE (autocuidado)...", end=" ", flush=True)

    prompt = prompt_autocuidado(state["consulta"])
    respuesta, tiempo = consultar_ollama(prompt, "autocuidado")
    print(f"✓ ({tiempo:.1f}s)")
    logger.info("Protocolo de autocuidado leve aplicado")

    return {
        "diagnostico": "✅ Síntomas leves — Manejables con autocuidado domiciliario.",
        "tratamiento": respuesta,
        "protocolo": "leve",
    }


# ============================================================
# ROUTER CONDICIONAL
# ============================================================

def router_urgencia(state: EstadoMedico) -> str:
    """Decide la ruta del workflow según el nivel de urgencia del triage."""
    nivel = state.get("nivel_urgencia", "MODERADO")
    print(f"\n   🗺️  Router → {nivel}")

    if nivel == "EMERGENCIA":
        return "emergencia"
    elif nivel == "LEVE":
        return "leve"
    else:
        return "paralelo"  # MODERADO o GRAVE → flujo completo en paralelo


# ============================================================
# CONSTRUCCIÓN DEL WORKFLOW LANGGRAPH
# ============================================================

def construir_workflow():
    """
    Grafo LangGraph con:
    - Triage → router condicional
    - EMERGENCIA → protocolo_emergencia (respuesta rápida)
    - LEVE       → protocolo_leve (autocuidado)
    - MODERADO/GRAVE → agente_paralelo (diagnóstico ∥ tratamiento)
    """
    workflow = StateGraph(EstadoMedico)

    workflow.add_node("triage", agente_triage)
    workflow.add_node("paralelo", agente_paralelo)
    workflow.add_node("emergencia", agente_protocolo_emergencia)
    workflow.add_node("leve", agente_protocolo_leve)

    workflow.set_entry_point("triage")

    workflow.add_conditional_edges(
        "triage",
        router_urgencia,
        {
            "paralelo": "paralelo",
            "emergencia": "emergencia",
            "leve": "leve",
        },
    )

    workflow.add_edge("paralelo", END)
    workflow.add_edge("emergencia", END)
    workflow.add_edge("leve", END)

    return workflow.compile()


# Compilar workflow una vez al importar el módulo
grafo_medico = construir_workflow()


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

def consultar(sintomas: str, nombre: str = "", edad: int = 0) -> Optional[dict]:
    """Función principal: ejecuta el workflow multiagente con caché y persistencia."""

    print(f"\n{'='*60}")
    print(f"🤖 SISTEMA MULTIAGENTE MÉDICO v3.0")
    print(f"📦 Modelo: {MODELO} | ⚡ Procesamiento paralelo activado")
    print(f"{'='*60}")
    print(f"\n📝 Síntomas: {sintomas}")

    # Verificar caché de consulta completa
    consulta_cached = cache_manager.get_consulta(sintomas, edad)
    if consulta_cached:
        print(f"\n⚡ RESPUESTA DESDE CACHÉ")
        _imprimir_resultado(consulta_cached)
        return consulta_cached

    # Crear paciente en BD
    paciente_id = db.crear_paciente(nombre if nombre else None, edad)
    print(f"👤 Paciente ID: {paciente_id}\n")

    inicio_total = time.time()

    try:
        resultado = grafo_medico.invoke(
            {
                "consulta": sintomas,
                "paciente_id": paciente_id,
                "edad": edad,
                "nombre": nombre,
                "triage": "",
                "diagnostico": "",
                "tratamiento": "",
                "nivel_urgencia": "",
                "tiempo_procesamiento": 0.0,
                "from_cache": False,
                "protocolo": "normal",
            }
        )

        tiempo_total = time.time() - inicio_total
        resultado["tiempo_procesamiento"] = tiempo_total

        # Persistir en BD
        consulta_id = db.guardar_consulta(
            {
                "paciente_id": paciente_id,
                "sintomas": sintomas,
                "triage": resultado.get("triage", ""),
                "diagnostico": resultado.get("diagnostico", ""),
                "tratamiento": resultado.get("tratamiento", ""),
                "nivel_urgencia": resultado.get("nivel_urgencia", ""),
                "protocolo": resultado.get("protocolo", "normal"),
                "tiempo_procesamiento": tiempo_total,
                "modelo_ia": MODELO,
                "from_cache": False,
            }
        )

        # Guardar en caché para consultas similares futuras
        cache_manager.set_consulta(sintomas, edad, resultado)

        _imprimir_resultado(resultado, tiempo_total, consulta_id)
        logger.info(
            f"Consulta completada en {tiempo_total:.1f}s | protocolo={resultado.get('protocolo')} | ID={consulta_id}"
        )

        return resultado

    except Exception as e:
        logger.error(f"Error en consulta: {e}")
        print(f"\n❌ Error: {e}")
        return None


def _imprimir_resultado(resultado: dict, tiempo: float = 0, consulta_id: int = None):
    """Imprime el resultado formateado en consola."""
    print(f"\n{'='*60}")
    print("📊 RESULTADOS")
    print(f"{'='*60}")
    print(f"\n🏥 TRIAGE\n{resultado.get('triage', 'N/A')}")
    print(f"\n🩺 DIAGNÓSTICO\n{resultado.get('diagnostico', 'N/A')}")
    print(f"\n💊 TRATAMIENTO\n{resultado.get('tratamiento', 'N/A')}")
    print(f"\n{'─'*60}")
    if tiempo:
        print(f"⏱️  Total: {tiempo:.1f}s | Protocolo: {resultado.get('protocolo', 'normal')}")
    if consulta_id:
        print(f"💾 Guardado en BD (ID: {consulta_id})")
    print(f"{'='*60}")


# ============================================================
# EJECUCIÓN DIRECTA (CLI)
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 SISTEMA MULTIAGENTE MÉDICO v3.0")
    print("   Paralelo | Rutas Condicionales | Caché | SQLite")
    print("=" * 60)

    while True:
        print("\n" + "-" * 30)
        print("1. 🔍 Nueva consulta médica")
        print("2. 📋 Ver consultas recientes")
        print("3. 📊 Estadísticas de caché")
        print("4. 🗑️  Limpiar caché")
        print("0. ❌ Salir")

        opcion = input("\nOpción: ").strip()

        if opcion == "1":
            sintomas = input("\n🩺 Síntomas: ").strip()
            if sintomas:
                nombre = input("👤 Nombre (opcional): ").strip()
                edad_input = input("📊 Edad (opcional): ").strip()
                edad = int(edad_input) if edad_input.isdigit() else 0
                consultar(sintomas, nombre, edad)
            else:
                print("❌ Ingresa síntomas válidos")

        elif opcion == "2":
            consultas = db.obtener_consultas(5)
            if consultas:
                print("\n📋 ÚLTIMAS CONSULTAS")
                for c in consultas:
                    print(f"\n  📅 {c['created_at'][:16]}")
                    print(f"  🩺 {c['sintomas'][:60]}...")
                    print(f"  🏥 {c.get('nivel_urgencia','N/D')} | {c.get('protocolo','normal')}")
            else:
                print("\n📂 No hay consultas registradas")

        elif opcion == "3":
            stats = cache_manager.get_stats()
            print(f"\n📊 CACHÉ: {stats}")

        elif opcion == "4":
            cache_manager.clear()
            print("\n🗑️  Caché limpiado")

        elif opcion == "0":
            db.close()
            print("\n👋 ¡Hasta luego!")
            break
