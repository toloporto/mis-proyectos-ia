# src/agents/sistema_multiagente_profesional.py
# SISTEMA MULTIAGENTE PROFESIONAL - PROMPTS OPTIMIZADOS Y CONTEXTO AVANZADO

import requests
import time
import json
from typing import TypedDict, List, Annotated
from datetime import datetime
from langgraph.graph import StateGraph, END
import operator

# ============================================
# CONFIGURACIÓN
# ============================================

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "antolin-dev:latest"  # O "llama3.1:latest"

# ============================================
# ESTADO MEJORADO CON CONTEXTO RICO
# ============================================

class EstadoMedicoProfesional(TypedDict):
    # Datos del paciente
    consulta: str
    edad: int
    sintomas_previos: List[str]
    
    # Resultados de agentes
    triage: str
    diagnostico: str
    medicamentos: str
    seguimiento: str
    especialista: str
    
    # Contexto y memoria
    nivel_urgencia: str
    factores_riesgo: List[str]
    alertas: List[str]
    
    # Historial y metadatos
    historial: Annotated[List[str], operator.add]
    timestamp: str
    version: str

# ============================================
# FUNCIÓN MEJORADA CON PROMPTS PROFESIONALES
# ============================================

def consultar_ollama(prompt: str, temperatura: float = 0.2, contexto_previo: str = "") -> str:
    """Consulta con prompts estructurados y contexto"""
    try:
        # Añadir contexto si existe
        if contexto_previo:
            prompt = f"Contexto previo: {contexto_previo}\n\n{prompt}"
        
        # Forzar formato estructurado
        prompt = prompt + "\n\nRESPONDE EN EL SIGUIENTE FORMATO:\n- Usa viñetas\n- Máximo 3 líneas\n- Sé específico"
        
        respuesta = requests.post(
            OLLAMA_URL,
            json={
                "model": MODELO,
                "prompt": prompt,
                "stream": False,
                "temperature": temperatura,
                "top_p": 0.9,
                "max_tokens": 150,
                "num_predict": 120
            },
            timeout=40
        )
        
        if respuesta.status_code == 200:
            resultado = respuesta.json()["response"].strip()
            # Limpiar respuestas con código
            if any(x in resultado for x in ["import", "def ", "class ", "```"]):
                return "Información médica disponible en consulta presencial"
            return resultado
        return "No se pudo procesar la consulta"
        
    except requests.exceptions.Timeout:
        return "Tiempo de espera agotado - Consulta médica presencial recomendada"
    except Exception as e:
        return f"Error en el sistema"

# ============================================
# AGENTE 1: TRIAGE PROFESIONAL
# ============================================

def agente_triage(state: EstadoMedicoProfesional):
    print("   🟡 [AGENTE 1/4] TRIAGE CLÍNICO: Evaluando urgencia...")
    
    prompt = f"""
Eres un médico de triage con 20 años de experiencia.

SÍNTOMAS DEL PACIENTE:
{state['consulta']}

EDAD: {state.get('edad', 'No especificada')} años

REALIZA UN ANÁLISIS CLÍNICO BASADO EN:
1. Signos de alarma (dificultad respiratoria, dolor torácico, alteración conciencia)
2. Factores de riesgo según edad
3. Tiempo de evolución sugerido

RESPONDE CON ESTA ESTRUCTURA EXACTA:
• NIVEL: [LEVE/MODERADO/GRAVE/EMERGENCIA]
• JUSTIFICACIÓN: [Razón clínica principal]
• PLAZO ATENCIÓN: [Inmediata/Urgente/24h/Programada]
• SEÑALES ALARMA: [Qué síntomas indican empeoramiento]
"""
    
    respuesta = consultar_ollama(prompt, 0.1)
    
    # Extraer nivel de urgencia para contexto
    nivel = "MODERADO"
    if "EMERGENCIA" in respuesta:
        nivel = "EMERGENCIA"
    elif "GRAVE" in respuesta:
        nivel = "GRAVE"
    elif "LEVE" in respuesta:
        nivel = "LEVE"
    
    return {
        "triage": f"🏥 TRIAGE CLÍNICO:\n{respuesta}",
        "nivel_urgencia": nivel,
        "historial": [f"✅ Triage: Nivel {nivel}", f"📋 {respuesta[:100]}"]
    }

# ============================================
# AGENTE 2: DIAGNÓSTICO DIFERENCIAL
# ============================================

def agente_diagnostico(state: EstadoMedicoProfesional):
    print("   🔵 [AGENTE 2/4] DIAGNÓSTICO DIFERENCIAL: Analizando...")
    
    prompt = f"""
Eres un médico internista especialista en diagnóstico diferencial.

SÍNTOMAS: {state['consulta']}
URGENCIA: {state.get('nivel_urgencia', 'No determinado')}

REALIZA UN DIAGNÓSTICO ESTRUCTURADO:

1. DIAGNÓSTICO PRINCIPAL: (1-2 opciones más probables)
2. DIAGNÓSTICOS DIFERENCIALES: (otras 2-3 posibilidades)
3. ESTUDIOS SUGERIDOS: (exámenes básicos para confirmar)
4. CONFIANZA DIAGNÓSTICA: [Alta/Media/Baja]

BASADO EN MEDICINA BASADA EN EVIDENCIA.
"""
    
    respuesta = consultar_ollama(prompt, 0.2)
    
    return {
        "diagnostico": f"🩺 DIAGNÓSTICO DIFERENCIAL:\n{respuesta}",
        "historial": [f"✅ Diagnóstico diferencial completado"]
    }

# ============================================
# AGENTE 3: PLAN TERAPÉUTICO
# ============================================

def agente_tratamiento(state: EstadoMedicoProfesional):
    print("   💊 [AGENTE 3/4] PLAN TERAPÉUTICO: Generando...")
    
    prompt = f"""
Eres un médico clínico diseñando un plan terapéutico.

DIAGNÓSTICO SUGERIDO:
{state.get('diagnostico', 'En evaluación')[:200]}

NIVEL DE URGENCIA: {state.get('nivel_urgencia', 'No determinado')}

DISEÑA UN PLAN EN 3 NIVELES:

PRIMER ESCALÓN (Inmediato - primeras horas):
• Medidas generales
• Fármacos de venta libre si aplican

SEGUNDO ESCALÓN (Primeras 48h):
• Seguimiento recomendado
• Signos de alarma a vigilar

TERCER ESCALÓN (Derivación):
• Cuándo acudir a urgencias
• Qué especialista podría requerir

PRIORIZA SEGURIDAD DEL PACIENTE.
"""
    
    respuesta = consultar_ollama(prompt, 0.25)
    
    return {
        "tratamiento": f"💊 PLAN TERAPÉUTICO:\n{respuesta}",
        "historial": [f"✅ Plan terapéutico generado"]
    }

# ============================================
# AGENTE 4: RESUMEN Y EDUCACIÓN PACIENTE
# ============================================

def agente_resumen(state: EstadoMedicoProfesional):
    print("   💡 [AGENTE 4/4] EDUCACIÓN PACIENTE: Creando resumen...")
    
    prompt = f"""
Eres un médico que debe explicar al paciente en lenguaje claro y sencillo.

TRADUCE ESTA INFORMACIÓN TÉCNICA A LENGUAJE CLARO:

RESUMEN CLÍNICO:
- Urgencia: {state.get('triage', 'N/A')[:150]}
- Diagnóstico: {state.get('diagnostico', 'N/A')[:150]}
- Plan: {state.get('tratamiento', 'N/A')[:150]}

EXPLICA AL PACIENTE EN 3 PUNTOS CLAROS:
1. QUÉ LE SUCEDE (explicación sencilla)
2. QUÉ PUEDE HACER AHORA (acciones prácticas)
3. CUÁNDO DEBE PREOCUPARSE (señales de alarma)

USA LENGUAJE CLARO, SIN JERGA MÉDICA COMPLEJA.
"""
    
    respuesta = consultar_ollama(prompt, 0.3)
    
    return {
        "historial": [f"💡 Resumen para paciente generado"],
        "contexto": [respuesta]
    }

# ============================================
# CONSTRUIR GRAFO OPTIMIZADO
# ============================================

def construir_sistema_profesional():
    workflow = StateGraph(EstadoMedicoProfesional)
    
    workflow.add_node("triage", agente_triage)
    workflow.add_node("diagnostico", agente_diagnostico)
    workflow.add_node("tratamiento", agente_tratamiento)
    workflow.add_node("resumen", agente_resumen)
    
    workflow.set_entry_point("triage")
    workflow.add_edge("triage", "diagnostico")
    workflow.add_edge("diagnostico", "tratamiento")
    workflow.add_edge("tratamiento", "resumen")
    workflow.add_edge("resumen", END)
    
    return workflow.compile()

# ============================================
# FUNCIÓN PRINCIPAL MEJORADA
# ============================================

def consulta_profesional(sintomas: str, edad: int = 0):
    """Consulta profesional con contexto mejorado"""
    
    print(f"\n{'='*60}")
    print(f"🏥 SISTEMA MULTIAGENTE PROFESIONAL")
    print(f"📋 PROMPTS CLÍNICOS OPTIMIZADOS")
    print(f"🔬 CONTEXTO AVANZADO ENTRE AGENTES")
    print(f"{'='*60}")
    print(f"\n📝 SÍNTOMAS: {sintomas}")
    if edad > 0:
        print(f"👤 EDAD: {edad} años")
    
    print(f"\n🤖 PROCESANDO CON 4 AGENTES ESPECIALIZADOS...")
    print(f"   🔄 TRIAGE → DIAGNÓSTICO → TRATAMIENTO → EDUCACIÓN\n")
    
    sistema = construir_sistema_profesional()
    
    estado_inicial = {
        "consulta": sintomas,
        "edad": edad,
        "sintomas_previos": [],
        "triage": "",
        "diagnostico": "",
        "medicamentos": "",
        "seguimiento": "",
        "especialista": "",
        "nivel_urgencia": "",
        "factores_riesgo": [],
        "alertas": [],
        "historial": [],
        "timestamp": datetime.now().isoformat(),
        "version": "2.0-profesional"
    }
    
    inicio = time.time()
    
    try:
        resultado = sistema.invoke(estado_inicial)
        tiempo = time.time() - inicio
        
        print(f"\n{'='*60}")
        print(f"📊 RESULTADOS CLÍNICOS")
        print(f"{'='*60}")
        
        print(f"\n🔴 AGENTE 1 - TRIAGE CLÍNICO:")
        print(f"{'─'*50}")
        print(f"{resultado.get('triage', 'N/A')}")
        
        print(f"\n🩺 AGENTE 2 - DIAGNÓSTICO DIFERENCIAL:")
        print(f"{'─'*50}")
        print(f"{resultado.get('diagnostico', 'N/A')}")
        
        print(f"\n💊 AGENTE 3 - PLAN TERAPÉUTICO:")
        print(f"{'─'*50}")
        print(f"{resultado.get('tratamiento', 'N/A')}")
        
        print(f"\n💡 AGENTE 4 - EDUCACIÓN PARA PACIENTE:")
        print(f"{'─'*50}")
        if resultado.get('contexto'):
            print(f"{resultado['contexto'][-1]}")
        else:
            print("Consulta médica presencial recomendada para educación personalizada")
        
        print(f"\n{'─'*50}")
        print(f"⏱️  TIEMPO TOTAL: {tiempo:.1f} segundos")
        print(f"🎯 MODELO: {MODELO}")
        print(f"🤖 AGENTES: 4 (Triage, Diagnóstico, Tratamiento, Educación)")
        print(f"="*60)
        
        # Guardar consulta
        guardar_consulta_profesional(sintomas, edad, resultado, tiempo)
        
        return resultado
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return None

# ============================================
# GUARDAR CONSULTAS PROFESIONALES
# ============================================

def guardar_consulta_profesional(sintomas: str, edad: int, resultado: dict, tiempo: float):
    """Guarda consultas con metadatos mejorados"""
    
    consulta = {
        "timestamp": datetime.now().isoformat(),
        "sintomas": sintomas,
        "edad": edad,
        "nivel_urgencia": resultado.get('nivel_urgencia', ''),
        "triage": resultado.get('triage', '')[:200],
        "diagnostico": resultado.get('diagnostico', '')[:200],
        "tratamiento": resultado.get('tratamiento', '')[:200],
        "tiempo_segundos": tiempo,
        "modelo": MODELO,
        "version": "2.0-profesional"
    }
    
    archivo = "/home/toloporto/proyectos/langGraph-Telemedicina/datos/consultas_profesionales.json"
    
    try:
        import os
        if os.path.exists(archivo):
            with open(archivo, 'r', encoding='utf-8') as f:
                historial = json.load(f)
        else:
            historial = []
        
        historial.append(consulta)
        
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(historial, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Consulta guardada en historial profesional")
        
    except Exception as e:
        print(f"\n⚠️ No se pudo guardar: {e}")

# ============================================
# MENÚ PRINCIPAL
# ============================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🌟 SISTEMA MULTIAGENTE MÉDICO PROFESIONAL v2.0")
    print("="*60)
    print("\nMEJORAS IMPLEMENTADAS:")
    print("  ✅ Prompts clínicos estructurados")
    print("  ✅ Contexto enriquecido entre agentes")
    print("  ✅ Diagnóstico diferencial formal")
    print("  ✅ Plan terapéutico por escalones")
    print("  ✅ Lenguaje claro para pacientes")
    print("  ✅ Persistencia con metadatos")
    
    while True:
        print("\n" + "="*40)
        print("📋 MENÚ PROFESIONAL")
        print("="*40)
        print("1. 🔍 Consulta médica completa")
        print("2. 📋 Ver historial profesional")
        print("3. ℹ️  Información del sistema")
        print("0. ❌ Salir")
        
        opcion = input("\nSelecciona: ")
        
        if opcion == "1":
            sintomas = input("\n🩺 Síntomas principales: ")
            if sintomas.strip():
                edad_input = input("📊 Edad del paciente (opcional, Enter para omitir): ")
                edad = int(edad_input) if edad_input.isdigit() else 0
                consulta_profesional(sintomas, edad)
            else:
                print("❌ Ingresa al menos un síntoma")
        
        elif opcion == "2":
            archivo = "/home/toloporto/proyectos/langGraph-Telemedicina/datos/consultas_profesionales.json"
            try:
                import os, json
                if os.path.exists(archivo):
                    with open(archivo, 'r') as f:
                        historial = json.load(f)
                    print(f"\n📋 ÚLTIMAS 5 CONSULTAS:")
                    for i, c in enumerate(historial[-5:], 1):
                        print(f"\n{i}. {c['timestamp'][:16]} - {c['sintomas'][:40]}...")
                        print(f"   Urgencia: {c.get('nivel_urgencia', 'N/D')}")
                else:
                    print("\n📂 No hay consultas previas")
            except Exception as e:
                print(f"Error: {e}")
        
        elif opcion == "3":
            print(f"\n📊 SISTEMA PROFESIONAL v2.0")
            print(f"   • Modelo: {MODELO}")
            print(f"   • Agentes: 4 especializados")
            print(f"   • Prompts: Clínicos estructurados")
            print(f"   • Contexto: Avanzado entre agentes")
        
        elif opcion == "0":
            print("\n👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")
