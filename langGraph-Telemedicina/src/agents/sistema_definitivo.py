# src/agents/sistema_phi3.py
# SISTEMA MULTIAGENTE CON PHI3 - BALANCE PERFECTO

import requests
import time
from typing import TypedDict
from datetime import datetime
from langgraph.graph import StateGraph, END

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "phi3:latest"  # 2.2GB - Buen balance velocidad/calidad

class EstadoMedico(TypedDict):
    consulta: str
    triage: str
    diagnostico: str
    tratamiento: str

def consultar_ollama(prompt: str) -> str:
    try:
        respuesta = requests.post(
            OLLAMA_URL,
            json={
                "model": MODELO,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.2,
                "max_tokens": 80,      # Reducido de 100 a 80
                "num_predict": 60       # Reducido de 80 a 60
            },
            timeout=30                  # Aumentado de 25 a 30 segundos
        )
        
        if respuesta.status_code == 200:
            resultado = respuesta.json()["response"].strip()
            # Limpiar respuestas
            if any(x in resultado for x in ["```", "import", "def "]):
                return "Consulta médica recomendada"
            if len(resultado) > 150:
                resultado = resultado[:147] + "..."
            return resultado if resultado else "Evaluación médica"
        return "Consulta médica"
        
    except requests.exceptions.Timeout:
        return "Consulta médica - Tiempo agotado"
    except:
        return "Evaluación médica recomendada"

def agente_triage(state: EstadoMedico):
    print("   🟡 [1/3] TRIAGE...", end=" ", flush=True)
    prompt = f"Síntomas: {state['consulta']}\nNivel de urgencia (LEVE/MODERADO/GRAVE/EMERGENCIA):"
    respuesta = consultar_ollama(prompt)
    print("✓")
    return {"triage": f"🏥 {respuesta}"}

def agente_diagnostico(state: EstadoMedico):
    print("   🔵 [2/3] DIAGNÓSTICO...", end=" ", flush=True)
    prompt = f"Síntomas: {state['consulta']}\nPosible diagnóstico en 1 frase:"
    respuesta = consultar_ollama(prompt)
    print("✓")
    return {"diagnostico": f"🩺 {respuesta}"}

def agente_tratamiento(state: EstadoMedico):
    print("   🟢 [3/3] TRATAMIENTO...", end=" ", flush=True)
    prompt = f"Para síntomas: {state['consulta']}\nRecomendación en 1 frase:"
    respuesta = consultar_ollama(prompt)
    print("✓")
    return {"tratamiento": f"💊 {respuesta}"}

def consultar(sintomas: str):
    print(f"\n{'='*50}")
    print(f"🤖 SISTEMA PHI3 - MULTIAGENTE")
    print(f"📦 Modelo: {MODELO} (2.2GB)")
    print(f"{'='*50}")
    print(f"\n📝 {sintomas}\n")
    
    workflow = StateGraph(EstadoMedico)
    workflow.add_node("triage", agente_triage)
    workflow.add_node("diagnostico", agente_diagnostico)
    workflow.add_node("tratamiento", agente_tratamiento)
    
    workflow.set_entry_point("triage")
    workflow.add_edge("triage", "diagnostico")
    workflow.add_edge("diagnostico", "tratamiento")
    workflow.add_edge("tratamiento", END)
    
    inicio = time.time()
    
    try:
        resultado = workflow.compile().invoke({
            "consulta": sintomas,
            "triage": "",
            "diagnostico": "",
            "tratamiento": ""
        })
        
        tiempo = time.time() - inicio
        
        print(f"\n{'='*50}")
        print(f"📊 RESULTADOS")
        print(f"{'='*50}")
        print(f"\n🔴 {resultado.get('triage', 'N/A')}")
        print(f"\n🩺 {resultado.get('diagnostico', 'N/A')}")
        print(f"\n💊 {resultado.get('tratamiento', 'N/A')}")
        print(f"\n{'─'*50}")
        print(f"⏱️  {tiempo:.1f}s | Modelo: phi3")
        print(f"{'='*50}")
        
        return resultado
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 SISTEMA MULTIAGENTE PHI3")
    print("⚡ Rápido | 🩺 Buena calidad | 3 agentes")
    print("="*50)
    
    while True:
        print("\n" + "-"*30)
        print("1. 🔍 Consulta médica")
        print("2. ℹ️  Info")
        print("0. ❌ Salir")
        
        opcion = input("\nOpción: ")
        
        if opcion == "1":
            sintomas = input("\n🩺 Síntomas: ")
            if sintomas.strip():
                consultar(sintomas)
            else:
                print("❌ Ingresa síntomas")
        
        elif opcion == "2":
            print(f"\n📊 SISTEMA PHI3")
            print(f"   Modelo: phi3:latest (2.2GB)")
            print(f"   Velocidad: ~20-30s")
            print(f"   Calidad: Buena para consultas médicas")
        
        elif opcion == "0":
            print("\n👋 ¡Hasta luego!")
            break