# src/agents/sistema_multiagente_ollama.py
# SISTEMA MULTIAGENTE CON OLLAMA - VERSIÓN RÁPIDA Y CONFIABLE

import requests
import json
from typing import TypedDict, List
from datetime import datetime
import time
from langgraph.graph import StateGraph, END

# Usar deepseek-coder (más rápido, 776MB, menos restricciones)
OLLAMA_URL = "http://localhost:11434/api/generate"
# MODELO = "deepseek-coder:latest"  # Más rápido y menos restricciones
# Alternativa: "antolin-dev:latest" si deepseek no funciona bien
MODELO = "llama3.1:latest"  # Tu modelo personalizado
#MODELO = "llama3.1:latest"  # Más lento pero mejor para medicina

class EstadoMedico(TypedDict):
    consulta: str
    triage: str
    diagnostico: str
    tratamiento: str
    historial: List[str]

def consultar_ollama(prompt: str, temperatura: float = 0.1) -> str:
    """Consulta Ollama con timeout más corto"""
    try:
        respuesta = requests.post(
            OLLAMA_URL,
            json={
                "model": MODELO,
                "prompt": prompt,
                "stream": False,
                "temperature": temperatura,
                "max_tokens": 150,  # Reducido para más velocidad
                "num_predict": 120
            },
            timeout=45  # Timeout más corto
        )
        
        if respuesta.status_code == 200:
            return respuesta.json()["response"].strip()
        else:
            return f"Error: {respuesta.status_code}"
            
    except requests.exceptions.Timeout:
        return "TIMEOUT - Respuesta muy larga, intenta síntomas más específicos"
    except requests.exceptions.ConnectionError:
        return "ERROR: Ollama no está corriendo"
    except Exception as e:
        return f"Error: {str(e)[:80]}"

# ============================================
# AGENTE 1: TRIAGE (versión más técnica)
# ============================================

def agente_triage(state: EstadoMedico):
    print("   🟡 [1/3] TRIAGE: Clasificando...")
    
    prompt = f"""Clasifica la severidad de estos síntomas en 3 niveles:

Síntomas: {state['consulta']}

Responde SOLO el nivel y razón (máx 10 palabras):
Respuesta:"""

    respuesta = consultar_ollama(prompt, temperatura=0.1)
    
    # Formatear para que se vea bien
    if "TIMEOUT" in respuesta or "ERROR" in respuesta:
        nivel = "⚠️ No se pudo clasificar"
    else:
        nivel = f"📋 {respuesta}"
    
    return {
        "triage": nivel,
        "historial": [f"✅ Triage - {datetime.now().strftime('%H:%M:%S')}"]
    }

# ============================================
# AGENTE 2: DIAGNÓSTICO (versión más técnica)
# ============================================

def agente_diagnostico(state: EstadoMedico):
    print("   🔵 [2/3] DIAGNÓSTICO: Evaluando...")
    
    prompt = f"""Posible diagnóstico para: {state['consulta']}
    
Responde en 1 línea corta (máx 15 palabras):"""

    respuesta = consultar_ollama(prompt, temperatura=0.2)
    
    return {
        "diagnostico": f"🩺 {respuesta}",
        "historial": [f"✅ Diagnóstico - {datetime.now().strftime('%H:%M:%S')}"]
    }

# ============================================
# AGENTE 3: TRATAMIENTO (versión más técnica)
# ============================================

def agente_tratamiento(state: EstadoMedico):
    print("   🟢 [3/3] TRATAMIENTO: Recomendando...")
    
    prompt = f"""Recomendación breve para: {state['consulta']}
    
Una frase corta (máx 12 palabras):"""

    respuesta = consultar_ollama(prompt, temperatura=0.2)
    
    return {
        "tratamiento": f"💊 {respuesta}",
        "historial": [f"✅ Tratamiento - {datetime.now().strftime('%H:%M:%S')}"]
    }

# ============================================
# CONSTRUIR GRAFO
# ============================================

def construir_sistema_multiagente():
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
# VERIFICAR OLLAMA
# ============================================

def verificar_ollama():
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            modelos = response.json().get("models", [])
            print(f"✅ Ollama conectado")
            print(f"✅ Usando modelo: {MODELO}")
            return True
        return False
    except:
        print("\n❌ Ollama no está corriendo")
        print("   Ejecuta en OTRA terminal: ollama serve")
        return False

# ============================================
# FUNCIÓN PRINCIPAL
# ============================================

def consultar_sistema_multiagente(sintomas: str):
    print(f"\n{'='*50}")
    print(f"🤖 SISTEMA MULTIAGENTE LANGGRAPH")
    print(f"{'='*50}")
    print(f"\n📝 Síntomas: {sintomas}")
    
    if not verificar_ollama():
        return None
    
    print(f"\n⚙️ PROCESANDO (3 agentes en cadena)...\n")
    
    sistema = construir_sistema_multiagente()
    
    estado_inicial = {
        "consulta": sintomas,
        "triage": "",
        "diagnostico": "",
        "tratamiento": "",
        "historial": []
    }
    
    inicio = time.time()
    
    try:
        resultado = sistema.invoke(estado_inicial)
        tiempo = time.time() - inicio
        
        print(f"\n{'='*50}")
        print(f"📊 RESULTADOS")
        print(f"{'='*50}")
        
        print(f"\n🔴 TRIAGE:\n   {resultado.get('triage', 'N/A')}")
        print(f"\n🩺 DIAGNÓSTICO:\n   {resultado.get('diagnostico', 'N/A')}")
        print(f"\n💊 TRATAMIENTO:\n   {resultado.get('tratamiento', 'N/A')}")
        
        print(f"\n{'─'*50}")
        print(f"⏱️  Tiempo: {tiempo:.1f}s | Modelo: {MODELO}")
        print(f"{'='*50}")
        
        return resultado
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None

# ============================================
# PROBAR RÁPIDO
# ============================================

if __name__ == "__main__":
    print("\n🚀 SISTEMA MULTIAGENTE LANGGRAPH + OLLAMA")
    print("   Modelo rápido: deepseek-coder")
    print("   3 agentes: TRIAGE → DIAGNÓSTICO → TRATAMIENTO\n")
    
    # Prueba directa sin menú
    sintomas = input("Describe tus síntomas: ")
    if sintomas.strip():
        consultar_sistema_multiagente(sintomas)
    else:
        # Prueba por defecto
        consultar_sistema_multiagente("Dolor de cabeza y fiebre")