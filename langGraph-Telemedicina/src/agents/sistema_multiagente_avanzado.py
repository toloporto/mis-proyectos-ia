# src/agents/sistema_multiagente_avanzado.py
# SISTEMA MULTIAGENTE AVANZADO - 6 AGENTES ESPECIALIZADOS

import requests
import time
import json
from typing import TypedDict, List, Annotated
from datetime import datetime
from langgraph.graph import StateGraph, END
import operator

# Configuración
OLLAMA_URL = "http://localhost:11434/api/generate"
#MODELO = "llama3.1:latest"  # Tu modelo actual
# Cambia el modelo en la línea 12 aproximadamente:
MODELO = "antolin-dev:latest"  # En lugar de llama3.1:latest

# ============================================
# ESTADO COMPARTIDO ENTRE AGENTES (MEMORIA)
# ============================================

class EstadoMedicoAvanzado(TypedDict):
    consulta: str                          # Síntomas originales
    triage: str                            # Nivel de urgencia
    diagnostico: str                       # Diagnóstico principal
    medicamentos: str                      # Medicamentos sugeridos
    seguimiento: str                       # Plan de seguimiento
    especialista: str                      # Derivación a especialista
    contexto: Annotated[List[str], operator.add]  # Memoria compartida
    timestamp: str                         # Fecha/hora

# ============================================
# FUNCIÓN PARA CONSULTAR OLLAMA
# ============================================

def consultar_ollama(prompt: str, temperatura: float = 0.2, rol: str = "") -> str:
    """Consulta Ollama - Versión optimizada para respuestas cortas"""
    try:
        # Forzar respuestas extremadamente cortas
        prompt = f"""{f"Como {rol}," if rol else ""} responde en MENOS DE 10 PALABRAS.
        
Pregunta: {prompt}

Respuesta corta:"""
        
        respuesta = requests.post(
            OLLAMA_URL,
            json={
                "model": MODELO,
                "prompt": prompt,
                "stream": False,
                "temperature": temperatura,
                "max_tokens": 50,       # Muy corto
                "num_predict": 40       # Muy corto
            },
            timeout=30                  # 30 segundos máximo
        )
        
        if respuesta.status_code == 200:
            resultado = respuesta.json()["response"].strip()
            # Limpiar respuestas que contengan código
            if "hashlib" in resultado or "import" in resultado or "```" in resultado:
                return "Consulta médica recomendada"
            # Limitar longitud
            if len(resultado) > 100:
                resultado = resultado[:97] + "..."
            return resultado
        return "Consulta médica"
        
    except requests.exceptions.Timeout:
        return "Consulta médica urgente"
    except Exception as e:
        return "Evaluación médica recomendada"

# ============================================
# AGENTE 1: TRIAGE (Clasifica urgencia)
# ============================================

def agente_triage(state: EstadoMedicoAvanzado):
    print("   🟡 [1/6] AGENTE TRIAGE: Evaluando urgencia...")
    
    prompt = f"""Clasifica la URGENCIA de estos síntomas en UNA palabra:

Síntomas: {state['consulta']}

Posibles respuestas SOLO: LEVE, MODERADO, GRAVE, o EMERGENCIA

Respuesta:"""
    
    respuesta = consultar_ollama(prompt, 0.1, "experto en triage médico")
    
    # Guardar en memoria compartida
    contexto_msg = f"📋 Triage: {respuesta} - Evaluación inicial completada"
    
    return {
        "triage": f"🏥 NIVEL DE URGENCIA: {respuesta}",
        "contexto": [contexto_msg],
        "timestamp": datetime.now().isoformat()
    }

# ============================================
# AGENTE 2: DIAGNÓSTICO (Identifica condición)
# ============================================

def agente_diagnostico(state: EstadoMedicoAvanzado):
    print("   🔵 [2/6] AGENTE DIAGNÓSTICO: Analizando condición...")
    
    prompt = f"""Basado en estos síntomas: {state['consulta']}
Y nivel de urgencia: {state.get('triage', 'No evaluado')}

Proporciona:
1. Diagnóstico principal (una frase)
2. Confianza (Alta/Media/Baja)

Formato: DIAGNÓSTICO: [texto] | CONFIANZA: [nivel]"""
    
    respuesta = consultar_ollama(prompt, 0.2, "médico diagnosticador")
    
    contexto_msg = f"🩺 Diagnóstico: {respuesta[:60]}..."
    
    return {
        "diagnostico": f"🩺 DIAGNÓSTICO: {respuesta}",
        "contexto": [contexto_msg]
    }

# ============================================
# AGENTE 3: MEDICAMENTOS (Sugiere tratamiento farmacológico)
# ============================================

def agente_medicamentos(state: EstadoMedicoAvanzado):
    print("   💊 [3/6] AGENTE MEDICAMENTOS: Recomendando fármacos...")
    
    prompt = f"""Para el diagnóstico: {state.get('diagnostico', 'No especificado')}
Síntomas: {state['consulta']}

Recomienda 1-2 medicamentos de venta libre (solo nombres genéricos):
Formato: 💊 [Nombre] - [para qué sirve en 5 palabras]"""
    
    respuesta = consultar_ollama(prompt, 0.3, "farmacólogo clínico")
    
    contexto_msg = f"💊 Medicamentos sugeridos: {respuesta[:50]}..."
    
    return {
        "medicamentos": f"💊 MEDICAMENTOS SUGERIDOS:\n   {respuesta}",
        "contexto": [contexto_msg]
    }

# ============================================
# AGENTE 4: SEGUIMIENTO (Plan de acción)
# ============================================

def agente_seguimiento(state: EstadoMedicoAvanzado):
    print("   📅 [4/6] AGENTE SEGUIMIENTO: Creando plan...")
    
    urgencia = state.get('triage', '')
    diagnostico = state.get('diagnostico', '')
    
    prompt = f"""Basado en:
Urgencia: {urgencia}
Diagnóstico: {diagnostico}

Crea un plan de seguimiento en 3 puntos:
1. Acción inmediata:
2. Próximas 24-48h:
3. Señales de alarma:"""
    
    respuesta = consultar_ollama(prompt, 0.25, "médico de seguimiento")
    
    contexto_msg = f"📅 Plan de seguimiento creado"
    
    return {
        "seguimiento": f"📅 PLAN DE SEGUIMIENTO:\n   {respuesta}",
        "contexto": [contexto_msg]
    }

# ============================================
# AGENTE 5: ESPECIALISTA (Derivación si es necesario)
# ============================================

def agente_especialista(state: EstadoMedicoAvanzado):
    print("   👨‍⚕️ [5/6] AGENTE ESPECIALISTA: Evaluando derivación...")
    
    urgencia = state.get('triage', '')
    diagnostico = state.get('diagnostico', '')
    
    prompt = f"""Basado en:
Urgencia: {urgencia}
Diagnóstico: {diagnostico}

¿Requiere derivación a especialista?
Responde SOLO: 
- NO NECESARIO, o
- SÍ: [Nombre del especialista] - [razón breve]"""
    
    respuesta = consultar_ollama(prompt, 0.2, "coordinador médico")
    
    contexto_msg = f"👨‍⚕️ Derivación: {respuesta[:50]}..."
    
    return {
        "especialista": f"👨‍⚕️ DERIVACIÓN A ESPECIALISTA:\n   {respuesta}",
        "contexto": [contexto_msg]
    }

# ============================================
# AGENTE 6: CONSEJO FINAL (Resumen y recomendación)
# ============================================

def agente_consejo_final(state: EstadoMedicoAvanzado):
    print("   💡 [6/6] AGENTE CONSEJO: Generando resumen final...")
    
    prompt = f"""Resume en 2 frases clave para el paciente basado en:
- Triage: {state.get('triage', '')}
- Diagnóstico: {state.get('diagnostico', '')}
- Seguimiento: {state.get('seguimiento', '')}

Respuesta:"""
    
    respuesta = consultar_ollama(prompt, 0.3, "consejero médico")
    
    return {
        "contexto": [f"💡 Consejo final: {respuesta[:80]}..."]
    }

# ============================================
# CONSTRUIR EL GRAFO MULTIAGENTE
# ============================================

def construir_sistema_multiagente():
    """Construye el grafo con 6 agentes en cadena"""
    
    workflow = StateGraph(EstadoMedicoAvanzado)
    
    # Añadir todos los agentes
    workflow.add_node("triage", agente_triage)
    workflow.add_node("diagnostico", agente_diagnostico)
    workflow.add_node("medicamentos", agente_medicamentos)
    workflow.add_node("seguimiento", agente_seguimiento)
    workflow.add_node("especialista", agente_especialista)
    workflow.add_node("consejo_final", agente_consejo_final)
    
    # Definir el flujo en cadena
    workflow.set_entry_point("triage")
    workflow.add_edge("triage", "diagnostico")
    workflow.add_edge("diagnostico", "medicamentos")
    workflow.add_edge("medicamentos", "seguimiento")
    workflow.add_edge("seguimiento", "especialista")
    workflow.add_edge("especialista", "consejo_final")
    workflow.add_edge("consejo_final", END)
    
    # Compilar
    app = workflow.compile()
    
    return app

# ============================================
# FUNCIÓN PRINCIPAL DE CONSULTA
# ============================================

def consultar_sistema_multiagente(sintomas: str):
    """Función principal con 6 agentes"""
    
    print(f"\n{'='*60}")
    print(f"🏥 SISTEMA MULTIAGENTE AVANZADO - 6 ESPECIALISTAS")
    print(f"📦 Modelo: {MODELO}")
    print(f"{'='*60}")
    print(f"\n📝 SÍNTOMAS DEL PACIENTE:")
    print(f"   \"{sintomas}\"")
    
    print(f"\n🤖 INICIANDO AGENTES EN CADENA...")
    print(f"   🔄 1→2→3→4→5→6\n")
    
    # Construir sistema
    sistema = construir_sistema_multiagente()
    
    # Estado inicial
    estado_inicial = {
        "consulta": sintomas,
        "triage": "",
        "diagnostico": "",
        "medicamentos": "",
        "seguimiento": "",
        "especialista": "",
        "contexto": [],
        "timestamp": ""
    }
    
    inicio = time.time()
    
    try:
        resultado = sistema.invoke(estado_inicial)
        tiempo_total = time.time() - inicio
        
        # Mostrar resultados
        print(f"\n{'='*60}")
        print(f"📊 RESULTADOS DEL SISTEMA (6 AGENTES ESPECIALIZADOS)")
        print(f"{'='*60}")
        
        print(f"\n🔴 AGENTE 1 - TRIAGE:")
        print(f"{'─'*50}")
        print(f"{resultado.get('triage', 'N/A')}")
        
        print(f"\n🩺 AGENTE 2 - DIAGNÓSTICO:")
        print(f"{'─'*50}")
        print(f"{resultado.get('diagnostico', 'N/A')}")
        
        print(f"\n💊 AGENTE 3 - MEDICAMENTOS:")
        print(f"{'─'*50}")
        print(f"{resultado.get('medicamentos', 'N/A')}")
        
        print(f"\n📅 AGENTE 4 - SEGUIMIENTO:")
        print(f"{'─'*50}")
        print(f"{resultado.get('seguimiento', 'N/A')}")
        
        print(f"\n👨‍⚕️ AGENTE 5 - ESPECIALISTA:")
        print(f"{'─'*50}")
        print(f"{resultado.get('especialista', 'N/A')}")
        
        print(f"\n💡 AGENTE 6 - CONSEJO FINAL:")
        print(f"{'─'*50}")
        if resultado.get('contexto'):
            ultimo_consejo = resultado['contexto'][-1] if resultado['contexto'] else "N/A"
            print(f"{ultimo_consejo}")
        
        print(f"\n{'─'*50}")
        print(f"⏱️  Tiempo total: {tiempo_total:.1f} segundos")
        print(f"🤖 Agentes ejecutados: 6 especialistas IA")
        print(f"📦 Modelo: {MODELO}")
        print(f"{'='*60}")
        
        # Guardar en archivo de log
        guardar_consulta(sintomas, resultado, tiempo_total)
        
        return resultado
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return None

# ============================================
# GUARDAR CONSULTAS EN ARCHIVO
# ============================================

def guardar_consulta(sintomas: str, resultado: dict, tiempo: float):
    """Guarda las consultas en un archivo JSON para historial"""
    
    consulta_data = {
        "timestamp": datetime.now().isoformat(),
        "sintomas": sintomas,
        "triage": resultado.get('triage', ''),
        "diagnostico": resultado.get('diagnostico', ''),
        "medicamentos": resultado.get('medicamentos', ''),
        "seguimiento": resultado.get('seguimiento', ''),
        "especialista": resultado.get('especialista', ''),
        "tiempo_segundos": tiempo,
        "modelo": MODELO
    }
    
    # Archivo de historial
    archivo = "/home/toloporto/proyectos/langGraph-Telemedicina/datos/consultas_multiagente.json"
    
    try:
        import os
        import json
        
        # Cargar existente o crear nuevo
        if os.path.exists(archivo):
            with open(archivo, 'r', encoding='utf-8') as f:
                historial = json.load(f)
        else:
            historial = []
        
        # Agregar nueva consulta
        historial.append(consulta_data)
        
        # Guardar
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(historial, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Consulta guardada en {archivo}")
        
    except Exception as e:
        print(f"\n⚠️ No se pudo guardar el historial: {e}")

# ============================================
# VER HISTORIAL DE CONSULTAS
# ============================================

def ver_historial():
    """Muestra el historial de consultas anteriores"""
    archivo = "/home/toloporto/proyectos/langGraph-Telemedicina/datos/consultas_multiagente.json"
    
    try:
        import os
        import json
        
        if not os.path.exists(archivo):
            print("\n📂 No hay consultas previas")
            return
        
        with open(archivo, 'r', encoding='utf-8') as f:
            historial = json.load(f)
        
        print(f"\n📋 HISTORIAL DE CONSULTAS ({len(historial)} registros)")
        print("="*50)
        
        for i, consulta in enumerate(historial[-5:], 1):  # Últimas 5
            print(f"\n{i}. {consulta['timestamp'][:16]}")
            print(f"   Síntomas: {consulta['sintomas'][:50]}...")
            print(f"   Diagnóstico: {consulta['diagnostico'][:60]}...")
            
    except Exception as e:
        print(f"Error al leer historial: {e}")

# ============================================
# MENÚ PRINCIPAL
# ============================================

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 SISTEMA MULTIAGENTE MÉDICO AVANZADO")
    print("   6 ESPECIALISTAS IA TRABAJANDO EN CADENA")
    print("="*50)
    print("\nAgentes disponibles:")
    print("   1️⃣ TRIAGE      - Clasifica urgencia")
    print("   2️⃣ DIAGNÓSTICO - Identifica condición")
    print("   3️⃣ MEDICAMENTOS - Sugiere fármacos")
    print("   4️⃣ SEGUIMIENTO - Crea plan de acción")
    print("   5️⃣ ESPECIALISTA - Deriva si es necesario")
    print("   6️⃣ CONSEJO FINAL - Resumen ejecutivo")
    
    while True:
        print("\n" + "="*30)
        print("📋 MENÚ PRINCIPAL")
        print("="*30)
        print("1. 🔍 Nueva consulta médica")
        print("2. 📋 Ver historial de consultas")
        print("3. ℹ️  Información del sistema")
        print("0. ❌ Salir")
        
        opcion = input("\nSelecciona: ")
        
        if opcion == "1":
            sintomas = input("\n🩺 Describe los síntomas: ")
            if sintomas.strip():
                consultar_sistema_multiagente(sintomas)
            else:
                print("❌ No ingresaste síntomas")
        
        elif opcion == "2":
            ver_historial()
        
        elif opcion == "3":
            print(f"\n📊 INFORMACIÓN DEL SISTEMA")
            print(f"   • Modelo: {MODELO}")
            print(f"   • Agentes: 6 especialistas")
            print(f"   • Flujo: TRIAGE → DIAGNÓSTICO → MEDICAMENTOS → SEGUIMIENTO → ESPECIALISTA → CONSEJO")
            print(f"   • Memoria compartida: Sí")
            print(f"   • Persistencia: JSON")
        
        elif opcion == "0":
            print("\n👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")
