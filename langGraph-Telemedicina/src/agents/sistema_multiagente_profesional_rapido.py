# src/agents/sistema_multiagente_profesional_rapido.py
# SISTEMA MULTIAGENTE PROFESIONAL - VERSIÓN RÁPIDA

import requests
import time
import json
from typing import TypedDict, List, Annotated
from datetime import datetime
from langgraph.graph import StateGraph, END
import operator

# ============================================
# CONFIGURACIÓN OPTIMIZADA
# ============================================

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "antolin-dev:latest"

# ============================================
# ESTADO SIMPLIFICADO PERO COMPLETO
# ============================================

class EstadoMedico(TypedDict):
    consulta: str
    edad: int
    triage: str
    diagnostico: str
    tratamiento: str
    educacion: str
    nivel_urgencia: str
    historial: List[str]
    timestamp: str

# ============================================
# FUNCIÓN RÁPIDA CON PROMPTS CORTOS
# ============================================

def consultar_ollama(prompt: str, temperatura: float = 0.2) -> str:
    """Consulta rápida con prompts cortos"""
    try:
        respuesta = requests.post(
            OLLAMA_URL,
            json={
                "model": MODELO,
                "prompt": prompt,
                "stream": False,
                "temperature": temperatura,
                "max_tokens": 100,
                "num_predict": 80
            },
            timeout=35
        )
        
        if respuesta.status_code == 200:
            resultado = respuesta.json()["response"].strip()
            # Limpiar respuestas
            if any(x in resultado for x in ["import", "def ", "```", "hashlib"]):
                return "Consulta médica recomendada"
            # Limitar longitud
            if len(resultado) > 200:
                resultado = resultado[:197] + "..."
            return resultado
        return "Consulta médica presencial"
        
    except requests.exceptions.Timeout:
        return "⚠️ Tiempo agotado - Prioridad: consulta médica"
    except Exception as e:
        return f"Evaluación médica recomendada"

# ============================================
# AGENTE 1: TRIAGE (RÁPIDO)
# ============================================

def agente_triage(state: EstadoMedico):
    print("   🟡 [1/4] TRIAGE...", end=" ", flush=True)
    
    prompt = f"""Paciente {state.get('edad', '?')} años. Síntomas: {state['consulta']}

Clasifica URGENCIA en 1 palabra (LEVE/MODERADO/GRAVE/EMERGENCIA) y da razón breve:"""
    
    respuesta = consultar_ollama(prompt, 0.1)
    print("✓")
    
    nivel = "MODERADO"
    if "EMERGENCIA" in respuesta:
        nivel = "EMERGENCIA"
    elif "GRAVE" in respuesta:
        nivel = "GRAVE"
    elif "LEVE" in respuesta:
        nivel = "LEVE"
    
    return {
        "triage": f"🏥 NIVEL: {respuesta}",
        "nivel_urgencia": nivel,
        "historial": [f"✅ Triage: {nivel}"]
    }

# ============================================
# AGENTE 2: DIAGNÓSTICO (RÁPIDO)
# ============================================

def agente_diagnostico(state: EstadoMedico):
    print("   🔵 [2/4] DIAGNÓSTICO...", end=" ", flush=True)
    
    prompt = f"""Síntomas: {state['consulta']}
Urgencia: {state.get('nivel_urgencia', 'N/D')}

Da 1 diagnóstico principal y 1 diferencial en 1 línea:"""
    
    respuesta = consultar_ollama(prompt, 0.2)
    print("✓")
    
    return {
        "diagnostico": f"🩺 {respuesta}",
        "historial": [f"✅ Diagnóstico completado"]
    }

# ============================================
# AGENTE 3: TRATAMIENTO (RÁPIDO)
# ============================================

def agente_tratamiento(state: EstadoMedico):
    print("   💊 [3/4] TRATAMIENTO...", end=" ", flush=True)
    
    prompt = f"""Para: {state['consulta']}
Diagnóstico: {state.get('diagnostico', '')[:100]}

Recomendación en 2 puntos (qué hacer ahora y cuándo ir a urgencias):"""
    
    respuesta = consultar_ollama(prompt, 0.25)
    print("✓")
    
    return {
        "tratamiento": f"💊 {respuesta}",
        "historial": [f"✅ Tratamiento generado"]
    }

# ============================================
# AGENTE 4: EDUCACIÓN PACIENTE (RÁPIDO)
# ============================================

def agente_educacion(state: EstadoMedico):
    print("   💡 [4/4] EDUCACIÓN...", end=" ", flush=True)
    
    prompt = f"""Explica al paciente en 1 frase clara y sencilla:
- Qué tiene
- Qué hacer
- Cuándo preocuparse

Síntomas: {state['consulta']}"""
    
    respuesta = consultar_ollama(prompt, 0.3)
    print("✓")
    
    return {
        "educacion": f"📋 CONSEJO: {respuesta}",
        "historial": [f"✅ Educación paciente"]
    }

# ============================================
# CONSTRUIR SISTEMA
# ============================================

def construir_sistema():
    workflow = StateGraph(EstadoMedico)
    
    workflow.add_node("triage", agente_triage)
    workflow.add_node("diagnostico", agente_diagnostico)
    workflow.add_node("tratamiento", agente_tratamiento)
    workflow.add_node("educacion", agente_educacion)
    
    workflow.set_entry_point("triage")
    workflow.add_edge("triage", "diagnostico")
    workflow.add_edge("diagnostico", "tratamiento")
    workflow.add_edge("tratamiento", "educacion")
    workflow.add_edge("educacion", END)
    
    return workflow.compile()

# ============================================
# CONSULTA PRINCIPAL
# ============================================

def consultar(sintomas: str, edad: int = 0):
    print(f"\n{'='*55}")
    print(f"🏥 SISTEMA MULTIAGENTE PROFESIONAL v2.1")
    print(f"📦 {MODELO} | ⚡ Modo rápido")
    print(f"{'='*55}")
    print(f"\n📝 {sintomas}")
    if edad > 0:
        print(f"👤 {edad} años")
    
    print(f"\n🔄 Ejecutando 4 agentes...\n")
    
    sistema = construir_sistema()
    
    estado = {
        "consulta": sintomas,
        "edad": edad,
        "triage": "",
        "diagnostico": "",
        "tratamiento": "",
        "educacion": "",
        "nivel_urgencia": "",
        "historial": [],
        "timestamp": datetime.now().isoformat()
    }
    
    inicio = time.time()
    
    try:
        resultado = sistema.invoke(estado)
        tiempo = time.time() - inicio
        
        print(f"\n{'='*55}")
        print(f"📊 RESULTADOS CLÍNICOS")
        print(f"{'='*55}")
        
        print(f"\n🔴 TRIAGE:\n   {resultado.get('triage', 'N/A')[:150]}")
        print(f"\n🩺 DIAGNÓSTICO:\n   {resultado.get('diagnostico', 'N/A')[:150]}")
        print(f"\n💊 TRATAMIENTO:\n   {resultado.get('tratamiento', 'N/A')[:150]}")
        print(f"\n📋 EDUCACIÓN:\n   {resultado.get('educacion', 'N/A')[:150]}")
        
        print(f"\n{'─'*55}")
        print(f"⏱️  {tiempo:.1f}s | ✅ 4 agentes ejecutados")
        print(f"{'='*55}")
        
        # Guardar
        guardar_consulta(sintomas, edad, resultado, tiempo)
        
        return resultado
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None

# ============================================
# GUARDAR CONSULTAS
# ============================================

def guardar_consulta(sintomas: str, edad: int, resultado: dict, tiempo: float):
    archivo = "/home/toloporto/proyectos/langGraph-Telemedicina/datos/consultas_profesionales.json"
    
    consulta = {
        "timestamp": datetime.now().isoformat(),
        "sintomas": sintomas,
        "edad": edad,
        "triage": resultado.get('triage', '')[:100],
        "diagnostico": resultado.get('diagnostico', '')[:100],
        "tratamiento": resultado.get('tratamiento', '')[:100],
        "tiempo": tiempo
    }
    
    try:
        historial = []
        import os
        if os.path.exists(archivo):
            with open(archivo, 'r') as f:
                historial = json.load(f)
        historial.append(consulta)
        with open(archivo, 'w') as f:
            json.dump(historial, f, indent=2)
        print(f"\n💾 Guardado")
    except:
        pass

# ============================================
# MENÚ
# ============================================

if __name__ == "__main__":
    print("\n" + "="*55)
    print("🌟 SISTEMA MULTIAGENTE MÉDICO v2.1")
    print("⚡ RÁPIDO | 🩺 PROFESIONAL | 🆓 GRATUITO")
    print("="*55)
    
    while True:
        print("\n" + "-"*30)
        print("1. 🔍 Consulta médica")
        print("2. ℹ️  Info")
        print("0. ❌ Salir")
        
        opcion = input("\nOpción: ")
        
        if opcion == "1":
            sintomas = input("\n🩺 Síntomas: ")
            if sintomas.strip():
                edad_input = input("📊 Edad (opcional): ")
                edad = int(edad_input) if edad_input.isdigit() else 0
                consultar(sintomas, edad)
            else:
                print("❌ Ingresa síntomas")
        
        elif opcion == "2":
            print(f"\n📊 SISTEMA v2.1")
            print(f"   Modelo: {MODELO}")
            print(f"   Agentes: 4 (Triage/Diagnóstico/Tratamiento/Educación)")
            print(f"   Timeout: 35s por agente")
        
        elif opcion == "0":
            print("\n👋 ¡Hasta luego!")
            break
