# src/agents/sistema_multiagente_rapido.py
# SISTEMA MULTIAGENTE RÁPIDO - 3 AGENTES OPTIMIZADOS

import requests
import time
from typing import TypedDict, List
from datetime import datetime
from langgraph.graph import StateGraph, END

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "antolin-dev:latest"  # Tu modelo más rápido

class EstadoMedico(TypedDict):
    consulta: str
    triage: str
    diagnostico: str
    tratamiento: str
    timestamp: str

def consultar_ollama(prompt: str) -> str:
    """Consulta rápida con respuestas muy cortas"""
    try:
        prompt = prompt + "\n\nRESPONDE EN 1 FRASE CORTA (max 12 palabras):"
        
        respuesta = requests.post(
            OLLAMA_URL,
            json={
                "model": MODELO,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.2,
                "max_tokens": 60,
                "num_predict": 50
            },
            timeout=25
        )
        
        if respuesta.status_code == 200:
            resultado = respuesta.json()["response"].strip()
            # Limpiar respuestas con código
            if any(x in resultado for x in ["hashlib", "import", "```", "def "]):
                return "Consulta médica recomendada"
            return resultado[:100]
        return "Consulta médica"
    except:
        return "Evaluación médica recomendada"

def agente_triage(state: EstadoMedico):
    print("   🟡 [1/3] TRIAGE...", end=" ", flush=True)
    prompt = f"¿Qué nivel de urgencia? (LEVE/MODERADO/GRAVE): {state['consulta']}"
    respuesta = consultar_ollama(prompt)
    print("✓")
    return {"triage": f"🏥 {respuesta}", "timestamp": datetime.now().isoformat()}

def agente_diagnostico(state: EstadoMedico):
    print("   🔵 [2/3] DIAGNÓSTICO...", end=" ", flush=True)
    prompt = f"Diagnóstico breve para: {state['consulta']}"
    respuesta = consultar_ollama(prompt)
    print("✓")
    return {"diagnostico": f"🩺 {respuesta}"}

def agente_tratamiento(state: EstadoMedico):
    print("   🟢 [3/3] TRATAMIENTO...", end=" ", flush=True)
    prompt = f"Recomendación para: {state['consulta']}"
    respuesta = consultar_ollama(prompt)
    print("✓")
    return {"tratamiento": f"💊 {respuesta}"}

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

def consultar(sintomas: str):
    print(f"\n{'='*50}")
    print(f"🤖 SISTEMA MULTIAGENTE RÁPIDO (3 agentes)")
    print(f"{'='*50}")
    print(f"\n📝 Síntomas: {sintomas}\n")
    
    sistema = construir_sistema()
    estado = {"consulta": sintomas, "triage": "", "diagnostico": "", "tratamiento": "", "timestamp": ""}
    
    inicio = time.time()
    try:
        resultado = sistema.invoke(estado)
        tiempo = time.time() - inicio
        
        print(f"\n{'='*50}")
        print(f"📊 RESULTADOS")
        print(f"{'='*50}")
        print(f"\n🔴 {resultado.get('triage', 'N/A')}")
        print(f"\n🩺 {resultado.get('diagnostico', 'N/A')}")
        print(f"\n💊 {resultado.get('tratamiento', 'N/A')}")
        print(f"\n{'─'*50}")
        print(f"⏱️  Tiempo: {tiempo:.1f}s")
        print(f"{'='*50}")
        return resultado
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("\n🚀 SISTEMA MULTIAGENTE RÁPIDO")
    sintomas = input("Describe tus síntomas: ")
    if sintomas:
        consultar(sintomas)
