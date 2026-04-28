# src/agents/sistema_phi3_db.py
# SISTEMA MULTIAGENTE CON BASE DE DATOS

import requests
import time
import sys
import os
from typing import TypedDict
from datetime import datetime
from langgraph.graph import StateGraph, END

# Añadir ruta para importar database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.database import db

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "phi3:latest"

class EstadoMedico(TypedDict):
    consulta: str
    paciente_id: int
    triage: str
    diagnostico: str
    tratamiento: str
    nivel_urgencia: str
    tiempos_agentes: list

def consultar_ollama(prompt: str, agente_nombre: str = "") -> str:
    """Consulta Ollama con logging"""
    try:
        inicio = time.time()
        respuesta = requests.post(
            OLLAMA_URL,
            json={
                "model": MODELO,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.2,
                "max_tokens": 100,
                "num_predict": 80
            },
            timeout=30
        )
        tiempo = time.time() - inicio
        
        if respuesta.status_code == 200:
            resultado = respuesta.json()["response"].strip()
            if len(resultado) > 150:
                resultado = resultado[:147] + "..."
            return resultado, tiempo
        return "Consulta médica", tiempo
        
    except requests.exceptions.Timeout:
        return "Consulta médica - Tiempo agotado", 30
    except Exception as e:
        return f"Error: {str(e)[:50]}", 0

def agente_triage(state: EstadoMedico):
    print("   🟡 [1/3] TRIAGE...", end=" ", flush=True)
    prompt = f"Síntomas: {state['consulta']}\nNivel de urgencia (LEVE/MODERADO/GRAVE/EMERGENCIA):"
    respuesta, tiempo = consultar_ollama(prompt, "triage")
    print(f"✓ ({tiempo:.1f}s)")
    
    # Extraer nivel
    nivel = "MODERADO"
    if "EMERGENCIA" in respuesta:
        nivel = "EMERGENCIA"
    elif "GRAVE" in respuesta:
        nivel = "GRAVE"
    elif "LEVE" in respuesta:
        nivel = "LEVE"
    
    state['tiempos_agentes'].append({"agente": "triage", "tiempo": tiempo, "respuesta": respuesta})
    
    return {"triage": f"🏥 {respuesta}", "nivel_urgencia": nivel}

def agente_diagnostico(state: EstadoMedico):
    print("   🔵 [2/3] DIAGNÓSTICO...", end=" ", flush=True)
    prompt = f"Síntomas: {state['consulta']}\nPosible diagnóstico en 1 frase:"
    respuesta, tiempo = consultar_ollama(prompt, "diagnostico")
    print(f"✓ ({tiempo:.1f}s)")
    
    state['tiempos_agentes'].append({"agente": "diagnostico", "tiempo": tiempo, "respuesta": respuesta})
    return {"diagnostico": f"🩺 {respuesta}"}

def agente_tratamiento(state: EstadoMedico):
    print("   🟢 [3/3] TRATAMIENTO...", end=" ", flush=True)
    prompt = f"Para síntomas: {state['consulta']}\nRecomendación en 1 frase:"
    respuesta, tiempo = consultar_ollama(prompt, "tratamiento")
    print(f"✓ ({tiempo:.1f}s)")
    
    state['tiempos_agentes'].append({"agente": "tratamiento", "tiempo": tiempo, "respuesta": respuesta})
    return {"tratamiento": f"💊 {respuesta}"}

def consultar(sintomas: str, nombre_paciente: str = "", edad: int = 0):
    print(f"\n{'='*55}")
    print(f"🤖 SISTEMA MULTIAGENTE CON BASE DE DATOS")
    print(f"📦 Modelo: {MODELO} | 💾 Guarda en SQLite")
    print(f"{'='*55}")
    print(f"\n📝 Síntomas: {sintomas}")
    
    # Crear paciente en BD
    paciente_id = db.crear_paciente(nombre_paciente, edad)
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
            "tiempos_agentes": []
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
        
        # Guardar logs de agentes
        for i, log in enumerate(resultado.get('tiempos_agentes', []), 1):
            db.guardar_agente_log({
                'consulta_id': consulta_id,
                'agente_nombre': log['agente'],
                'agente_respuesta': log['respuesta'],
                'tiempo_ejecucion': log['tiempo'],
                'orden': i
            })
        
        print(f"\n{'='*55}")
        print(f"📊 RESULTADOS")
        print(f"{'='*55}")
        print(f"\n🔴 {resultado.get('triage', 'N/A')}")
        print(f"\n🩺 {resultado.get('diagnostico', 'N/A')}")
        print(f"\n💊 {resultado.get('tratamiento', 'N/A')}")
        print(f"\n{'─'*55}")
        print(f"⏱️  Total: {tiempo_total:.1f}s")
        print(f"💾 Guardado en BD (ID: {consulta_id})")
        print(f"{'='*55}")
        
        return resultado
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None

def mostrar_estadisticas():
    """Muestra estadísticas desde la base de datos"""
    stats = db.obtener_estadisticas()
    print(f"\n📊 ESTADÍSTICAS DEL SISTEMA")
    print(f"   Total consultas: {stats.get('total_consultas', 0)}")
    print(f"   Total pacientes: {stats.get('total_pacientes', 0)}")
    print(f"   Tiempo promedio: {stats.get('tiempo_promedio', 0):.1f}s")
    print(f"\n   Distribución por urgencia:")
    for u in stats.get('urgencias', []):
        print(f"     • {u['nivel_urgencia']}: {u['cantidad']}")

def mostrar_ultimas_consultas():
    """Muestra las últimas consultas"""
    consultas = db.obtener_consultas(5)
    if not consultas:
        print("\n📂 No hay consultas registradas")
        return
    
    print(f"\n📋 ÚLTIMAS 5 CONSULTAS")
    for c in consultas:
        print(f"\n   📅 {c['created_at'][:16]}")
        print(f"   🩺 {c['sintomas'][:50]}...")
        print(f"   🏥 {c.get('nivel_urgencia', 'N/D')}")

if __name__ == "__main__":
    print("\n" + "="*55)
    print("🚀 SISTEMA MULTIAGENTE CON BASE DE DATOS")
    print("   SQLite | 3 agentes | Persistencia total")
    print("="*55)
    
    while True:
        print("\n" + "-"*30)
        print("1. 🔍 Nueva consulta médica")
        print("2. 📊 Ver estadísticas")
        print("3. 📋 Últimas consultas")
        print("4. ℹ️  Info sistema")
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
            mostrar_estadisticas()
        
        elif opcion == "3":
            mostrar_ultimas_consultas()
        
        elif opcion == "4":
            print(f"\n📊 SISTEMA CON BD")
            print(f"   Modelo: {MODELO}")
            print(f"   Base de datos: SQLite")
            print(f"   Ubicación: datos/consultas.db")
            print(f"   Tablas: pacientes, consultas, agentes_log, metricas")
        
        elif opcion == "0":
            db.close()
            print("\n👋 ¡Hasta luego!")
            break