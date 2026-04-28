# src/agents/sistema_phi3_db.py
"""Sistema multiagente con caché y logging profesional"""

import requests
import time
import sys
import os
from typing import TypedDict, Dict, Any
from datetime import datetime
from langgraph.graph import StateGraph, END

# Añadir ruta para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import db
from cache.cache_manager import cache_manager
from utils.logger import get_logger
from config.settings import settings

# Configuración
OLLAMA_URL = settings.OLLAMA_URL
MODELO = settings.DEFAULT_MODEL
TIMEOUT = settings.MODEL_TIMEOUT

# Logger
logger = get_logger("multiagente")

class EstadoMedico(TypedDict):
    consulta: str
    paciente_id: int
    triage: str
    diagnostico: str
    tratamiento: str
    nivel_urgencia: str
    tiempos_agentes: list
    from_cache: bool

def consultar_ollama(prompt: str, agente_nombre: str = "") -> tuple:
    """Consulta Ollama con logging y caché"""
    try:
        inicio = time.time()
        logger.debug(f"Consultando {agente_nombre}...")
        
        respuesta = requests.post(
            OLLAMA_URL,
            json={
                "model": MODELO,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.2,
                "max_tokens": settings.MAX_TOKENS,
                "num_predict": settings.MAX_TOKENS - 20
            },
            timeout=TIMEOUT
        )
        tiempo = time.time() - inicio
        
        if respuesta.status_code == 200:
            resultado = respuesta.json()["response"].strip()
            # Limpiar respuestas con código
            if any(x in resultado for x in ["import", "def ", "```", "class "]):
                resultado = "Consulta médica recomendada"
            if len(resultado) > 200:
                resultado = resultado[:197] + "..."
            logger.info(f"{agente_nombre} completado en {tiempo:.1f}s")
            return resultado, tiempo
        return f"Error: {respuesta.status_code}", tiempo
        
    except requests.exceptions.Timeout:
        logger.warning(f"Timeout en {agente_nombre} después de {TIMEOUT}s")
        return "Consulta médica - Tiempo agotado", TIMEOUT
    except Exception as e:
        logger.error(f"Error en {agente_nombre}: {e}")
        return f"Error: {str(e)[:50]}", 0

def agente_triage(state: EstadoMedico):
    """Agente de triage con caché"""
    print("   🟡 [1/3] TRIAGE...", end=" ", flush=True)
    
    # Verificar caché primero
    cache_key = f"triage_{state['consulta'].lower().strip()}"
    cached = cache_manager.get(cache_key)
    
    if cached and not state.get('from_cache', False):
        print("✓ (desde caché)")
        respuesta = cached
        tiempo = 0
    else:
        prompt = f"Síntomas: {state['consulta']}\nNivel de urgencia (LEVE/MODERADO/GRAVE/EMERGENCIA):"
        respuesta, tiempo = consultar_ollama(prompt, "triage")
        # Guardar en caché
        cache_manager.set(cache_key, respuesta, 3600)
        print(f"✓ ({tiempo:.1f}s)")
    
    # Extraer nivel
    nivel = "MODERADO"
    if "EMERGENCIA" in respuesta:
        nivel = "EMERGENCIA"
    elif "GRAVE" in respuesta:
        nivel = "GRAVE"
    elif "LEVE" in respuesta:
        nivel = "LEVE"
    
    logger.info(f"Triage: {nivel} - {respuesta[:50]}")
    
    return {"triage": f"🏥 {respuesta}", "nivel_urgencia": nivel}

def agente_diagnostico(state: EstadoMedico):
    """Agente de diagnóstico"""
    print("   🔵 [2/3] DIAGNÓSTICO...", end=" ", flush=True)
    
    prompt = f"Síntomas: {state['consulta']}\nPosible diagnóstico en 1 frase:"
    respuesta, tiempo = consultar_ollama(prompt, "diagnostico")
    print(f"✓ ({tiempo:.1f}s)")
    
    logger.info(f"Diagnóstico: {respuesta[:80]}...")
    
    return {"diagnostico": f"🩺 {respuesta}"}

def agente_tratamiento(state: EstadoMedico):
    """Agente de tratamiento"""
    print("   🟢 [3/3] TRATAMIENTO...", end=" ", flush=True)
    
    prompt = f"Para síntomas: {state['consulta']}\nRecomendación en 1 frase:"
    respuesta, tiempo = consultar_ollama(prompt, "tratamiento")
    print(f"✓ ({tiempo:.1f}s)")
    
    logger.info(f"Tratamiento: {respuesta[:80]}...")
    
    return {"tratamiento": f"💊 {respuesta}"}

def consultar(sintomas: str, nombre_paciente: str = "", edad: int = 0):
    """Función principal con caché integrado"""
    
    print(f"\n{'='*55}")
    print(f"🤖 SISTEMA MULTIAGENTE CON CACHÉ")
    print(f"📦 Modelo: {MODELO} | ⚡ Caché activado")
    print(f"{'='*55}")
    print(f"\n📝 Síntomas: {sintomas}")
    
    # Verificar caché de consulta completa
    consulta_cache = cache_manager.get_consulta(sintomas, edad)
    
    if consulta_cache:
        print(f"\n⚡ RESPUESTA DESDE CACHÉ (más rápido)")
        print(f"\n🔴 {consulta_cache.get('triage', 'N/A')}")
        print(f"\n🩺 {consulta_cache.get('diagnostico', 'N/A')}")
        print(f"\n💊 {consulta_cache.get('tratamiento', 'N/A')}")
        print(f"\n{'─'*55}")
        print(f"⏱️  Tiempo: < 1s (desde caché)")
        return consulta_cache
    
    # Crear paciente en BD
    paciente_id = db.crear_paciente(nombre_paciente if nombre_paciente else None, edad)
    print(f"👤 Paciente ID: {paciente_id}")
    
    print(f"\n🔄 Ejecutando 3 agentes...\n")
    
    workflow = StateGraph(EstadoMedico)
    workflow.add_node("triage", agente_triage)
    workflow.add_node("diagnostico", agente_diagnostico)
    workflow.add_node("tratamiento", agente_tratamiento)
    
    workflow.set_entry_point("triage")
    workflow.add_edge("triage", "diagnostico")
    workflow.add_edge("diagnostico", "tratamiento")
    workflow.add_edge("tratamiento", END)
    
    inicio_total = time.time()
    
    try:
        resultado = workflow.compile().invoke({
            "consulta": sintomas,
            "paciente_id": paciente_id,
            "triage": "",
            "diagnostico": "",
            "tratamiento": "",
            "nivel_urgencia": "",
            "tiempos_agentes": [],
            "from_cache": False
        })
        
        tiempo_total = time.time() - inicio_total
        
        # Guardar en base de datos
        consulta_id = db.guardar_consulta({
            'paciente_id': paciente_id,
            'sintomas': sintomas,
            'triage': resultado.get('triage', ''),
            'diagnostico': resultado.get('diagnostico', ''),
            'tratamiento': resultado.get('tratamiento', ''),
            'nivel_urgencia': resultado.get('nivel_urgencia', ''),
            'tiempo_procesamiento': tiempo_total,
            'modelo_ia': MODELO
        })
        
        # Guardar en caché para futuras consultas similares
        cache_manager.set_consulta(sintomas, edad, resultado)
        
        print(f"\n{'='*55}")
        print(f"📊 RESULTADOS")
        print(f"{'='*55}")
        print(f"\n🔴 {resultado.get('triage', 'N/A')}")
        print(f"\n🩺 {resultado.get('diagnostico', 'N/A')}")
        print(f"\n💊 {resultado.get('tratamiento', 'N/A')}")
        print(f"\n{'─'*55}")
        print(f"⏱️  Total: {tiempo_total:.1f}s")
        print(f"💾 Guardado en BD (ID: {consulta_id})")
        print(f"⚡ Caché activado para consultas similares")
        print(f"{'='*55}")
        
        logger.info(f"Consulta completada en {tiempo_total:.1f}s para paciente {paciente_id}")
        
        return resultado
        
    except Exception as e:
        logger.error(f"Error en consulta: {e}")
        print(f"\n❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("\n" + "="*55)
    print("🚀 SISTEMA MULTIAGENTE CON CACHÉ")
    print("   SQLite | Caché en memoria | Logs profesionales")
    print("="*55)
    
    while True:
        print("\n" + "-"*30)
        print("1. 🔍 Nueva consulta médica")
        print("2. 📋 Ver consultas recientes")
        print("3. 📊 Estadísticas caché")
        print("4. 🗑️ Limpiar caché")
        print("0. ❌ Salir")
        
        opcion = input("\nOpción: ")
        
        if opcion == "1":
            sintomas = input("\n🩺 Síntomas: ")
            if sintomas.strip():
                nombre = input("👤 Nombre (opcional): ")
                edad_input = input("📊 Edad (opcional): ")
                edad = int(edad_input) if edad_input.isdigit() else 0
                consultar(sintomas, nombre, edad)
            else:
                print("❌ Ingresa síntomas")
        
        elif opcion == "2":
            consultas = db.obtener_consultas(5)
            if consultas:
                print("\n📋 ÚLTIMAS CONSULTAS")
                for c in consultas:
                    print(f"\n   📅 {c['created_at'][:16]}")
                    print(f"   🩺 {c['sintomas'][:50]}...")
                    print(f"   🏥 {c.get('nivel_urgencia', 'N/D')}")
            else:
                print("\n📂 No hay consultas registradas")
        
        elif opcion == "3":
            stats = cache_manager.get_stats()
            print(f"\n📊 ESTADÍSTICAS DEL CACHÉ")
            print(f"   Tipo: {stats['type']}")
            print(f"   Claves almacenadas: {stats['keys']}")
            print(f"   Estado: {stats['status']}")
        
        elif opcion == "4":
            cache_manager.clear()
            print("\n🗑️ Caché limpiado correctamente")
        
        elif opcion == "0":
            db.close()
            print("\n👋 ¡Hasta luego!")
            break
