# src/agents/sistema_multiagente_medico.py
# SISTEMA MULTIAGENTE MÉDICO - VERSIÓN ESPECIALIZADA

import requests
import time
from typing import TypedDict, List
from datetime import datetime
from langgraph.graph import StateGraph, END

OLLAMA_URL = "http://localhost:11434/api/generate"

# Probar modelos en orden de preferencia
MODELOS_PREFERIDOS = ["llama3.1:latest"]

class EstadoMedico(TypedDict):
    consulta: str
    triage: str
    diagnostico: str
    tratamiento: str
    advice: str
    historial: List[str]

def consultar_ollama(prompt: str, modelo: str, temperatura: float = 0.3) -> str:
    """Consulta Ollama con timeout razonable"""
    try:
        respuesta = requests.post(
            OLLAMA_URL,
            json={
                "model": modelo,
                "prompt": prompt,
                "stream": False,
                "temperature": temperatura,
                "max_tokens": 100,
                "num_predict": 150
            },
            timeout=20
        )
        
        if respuesta.status_code == 200:
            return respuesta.json()["response"].strip()
        return f"Error: {respuesta.status_code}"
    except Exception as e:
        return f"Error: {str(e)[:60]}"

def encontrar_modelo_funcional():
    """Encuentra el primer modelo que funcione"""
    for modelo in MODELOS_PREFERIDOS:
        try:
            respuesta = requests.post(
                OLLAMA_URL,
                json={"model": modelo, "prompt": "Hola", "stream": False},
                timeout=10
            )
            if respuesta.status_code == 200:
                return modelo
        except:
            continue
    return "llama3.1:latest"  # Default

# ============================================
# AGENTE 1: TRIAGE MÉDICO
# ============================================

def agente_triage(state: EstadoMedico):
    print("   🟡 [1/3] TRIAGE: Analizando urgencia...")
    
    prompt = f"""Como asistente médico, clasifica la URGENCIA de estos síntomas en una palabra:

Síntomas: {state['consulta']}

Responde SOLO con: LEVE, MODERADO, o GRAVE

Respuesta:"""

    modelo = encontrar_modelo_funcional()
    respuesta = consultar_ollama(prompt, modelo, 0.1)
    
    return {
        "triage": f"🏥 NIVEL DE URGENCIA: {respuesta}",
        "historial": [f"✅ Triage: {respuesta}"]
    }

# ============================================
# AGENTE 2: DIAGNÓSTICO
# ============================================

def agente_diagnostico(state: EstadoMedico):
    print("   🔵 [2/3] DIAGNÓSTICO: Evaluando...")
    
    prompt = f"""Como asistente médico, posible diagnóstico para:
{state['consulta']}

Una frase corta (máx 15 palabras):"""

    modelo = encontrar_modelo_funcional()
    respuesta = consultar_ollama(prompt, modelo, 0.2)
    
    return {
        "diagnostico": f"🩺 POSIBLE DIAGNÓSTICO: {respuesta}",
        "historial": [f"✅ Diagnóstico completado"]
    }

# ============================================
# AGENTE 3: RECOMENDACIÓN
# ============================================

def agente_tratamiento(state: EstadoMedico):
    print("   🟢 [3/3] RECOMENDACIÓN: Sugiriendo acciones...")
    
    prompt = f"""Como asistente médico, recomendación breve para:
{state['consulta']}

Una frase de acción (máx 12 palabras):"""

    modelo = encontrar_modelo_funcional()
    respuesta = consultar_ollama(prompt, modelo, 0.2)
    
    return {
        "tratamiento": f"💊 RECOMENDACIÓN: {respuesta}",
        "historial": [f"✅ Recomendación generada"]
    }

# ============================================
# CONSTRUIR SISTEMA
# ============================================

def construir_sistema():
    workflow = StateGraph(EstadoMedico)
    
    workflow.add_node("triage", agente_triage)
    workflow.add_node("diagnostico", agente_diagnostico)
    workflow.add_node("tratamiento", agente_tratamiento)
    
    workflow.set_entry_point("triage")
    workflow.add_edge("triage", "diagnostico")
    workflow.add_edge("diagnostico", "tratamiento")
    workflow.add_edge("tratamiento", END)
    
    return workflow.compile()

# ============================================
# CONSULTAR SISTEMA
# ============================================

def consultar_sistema(sintomas: str):
    modelo = encontrar_modelo_funcional()
    
    print(f"\n{'='*50}")
    print(f"🤖 SISTEMA MULTIAGENTE MÉDICO")
    print(f"📦 Modelo: {modelo}")
    print(f"{'='*50}")
    print(f"\n📝 Síntomas: {sintomas}")
    
    print(f"\n⚙️ Ejecutando 3 agentes en cadena...\n")
    
    sistema = construir_sistema()
    
    estado_inicial = {
        "consulta": sintomas,
        "triage": "",
        "diagnostico": "",
        "tratamiento": "",
        "advice": "",
        "historial": []
    }
    
    inicio = time.time()
    
    try:
        resultado = sistema.invoke(estado_inicial)
        tiempo = time.time() - inicio
        
        print(f"\n{'='*50}")
        print(f"📊 RESULTADOS DE LOS 3 AGENTES")
        print(f"{'='*50}")
        
        print(f"\n🔴 AGENTE 1 - TRIAGE:")
        print(f"   {resultado.get('triage', 'N/A')}")
        
        print(f"\n🩺 AGENTE 2 - DIAGNÓSTICO:")
        print(f"   {resultado.get('diagnostico', 'N/A')}")
        
        print(f"\n💊 AGENTE 3 - TRATAMIENTO:")
        print(f"   {resultado.get('tratamiento', 'N/A')}")
        
        print(f"\n{'─'*50}")
        print(f"⏱️  Tiempo total: {tiempo:.1f}s")
        print(f"✅ Consulta procesada por 3 agentes IA")
        print(f"{'='*50}")
        
        return resultado
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("\n🚀 SISTEMA MULTIAGENTE MÉDICO CON LANGGRAPH")
    print("   3 agentes IA trabajan en cadena:\n")
    print("   1️⃣ TRIAGE → 2️⃣ DIAGNÓSTICO → 3️⃣ TRATAMIENTO\n")
    
    sintomas = input("Describe tus síntomas: ")
    if sintomas.strip():
        consultar_sistema(sintomas)
