# src/agents/sistema_tinyllama.py
# SISTEMA MULTIAGENTE CON TINYLLAMA - ULTRA RÁPIDO

import requests
import time
from typing import TypedDict
from datetime import datetime
from langgraph.graph import StateGraph, END

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "tinyllama:latest"  # 637MB - Ultra rápido

class EstadoMedico(TypedDict):
    consulta: str
    triage: str
    diagnostico: str
    tratamiento: str
    timestamp: str

def consultar_ollama(prompt: str) -> str:
    """Consulta rápida para TinyLlama"""
    try:
        respuesta = requests.post(
            OLLAMA_URL,
            json={
                "model": MODELO,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.1,
                "max_tokens": 60,
                "num_predict": 50
            },
            timeout=15  # TinyLlama es muy rápido
        )
        
        if respuesta.status_code == 200:
            resultado = respuesta.json()["response"].strip()
            # Limpiar respuestas
            if len(resultado) > 100:
                resultado = resultado[:97] + "..."
            return resultado if resultado else "Consulta médica"
        return "Consulta médica"
        
    except requests.exceptions.Timeout:
        return "Consulta médica urgente"
    except Exception as e:
        return "Evaluación médica"

def agente_triage(state: EstadoMedico):
    print("   🟡 [1/3] TRIAGE...", end=" ", flush=True)
    
    prompt = f"""Sintomas: {state['consulta']}
Nivel urgencia (LEVE/MODERADO/GRAVE):"""
    
    respuesta = consultar_ollama(prompt)
    print("✓")
    return {"triage": f"🏥 {respuesta}"}

def agente_diagnostico(state: EstadoMedico):
    print("   🔵 [2/3] DIAGNÓSTICO...", end=" ", flush=True)
    
    prompt = f"""Sintomas: {state['consulta']}
Diagnostico breve 1 frase:"""
    
    respuesta = consultar_ollama(prompt)
    print("✓")
    return {"diagnostico": f"🩺 {respuesta}"}

def agente_tratamiento(state: EstadoMedico):
    print("   🟢 [3/3] TRATAMIENTO...", end=" ", flush=True)
    
    prompt = f"""Para: {state['consulta']}
Recomendacion 1 frase:"""
    
    respuesta = consultar_ollama(prompt)
    print("✓")
    return {"tratamiento": f"💊 {respuesta}"}

def consultar(sintomas: str):
    print(f"\n{'='*50}")
    print(f"⚡ SISTEMA TINYLLAMA - MULTIAGENTE RÁPIDO")
    print(f"📦 Modelo: {MODELO} (637MB)")
    print(f"{'='*50}")
    print(f"\n📝 Síntomas: {sintomas}")
    print(f"\n🔄 Ejecutando 3 agentes...\n")
    
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
            "tratamiento": "",
            "timestamp": datetime.now().isoformat()
        })
        
        tiempo = time.time() - inicio
        
        print(f"\n{'='*50}")
        print(f"📊 RESULTADOS")
        print(f"{'='*50}")
        print(f"\n🔴 {resultado.get('triage', 'N/A')}")
        print(f"\n🩺 {resultado.get('diagnostico', 'N/A')}")
        print(f"\n💊 {resultado.get('tratamiento', 'N/A')}")
        print(f"\n{'─'*50}")
        print(f"⏱️  Tiempo: {tiempo:.1f} segundos")
        print(f"✅ 3 agentes ejecutados")
        print(f"{'='*50}")
        
        return resultado
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 SISTEMA MULTIAGENTE TINYLLAMA")
    print("⚡ Ultra rápido | 637MB | 3 agentes")
    print("="*50)
    
    while True:
        print("\n" + "-"*30)
        print("1. 🔍 Consulta médica")
        print("2. ℹ️  Información")
        print("0. ❌ Salir")
        
        opcion = input("\nOpción: ")
        
        if opcion == "1":
            sintomas = input("\n🩺 Describe tus síntomas: ")
            if sintomas.strip():
                consultar(sintomas)
            else:
                print("❌ Ingresa síntomas")
        
        elif opcion == "2":
            print(f"\n📊 SISTEMA:")
            print(f"   Modelo: tinyllama:latest (637MB)")
            print(f"   Agentes: 3 (Triage/Diagnóstico/Tratamiento)")
            print(f"   Timeout: 15 segundos por agente")
            print(f"   Velocidad: Ultra rápida")
        
        elif opcion == "0":
            print("\n👋 ¡Hasta luego!")
            break
