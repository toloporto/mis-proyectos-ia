# src/agents/sistema_multiagente.py
# SISTEMA MULTIAGENTE REAL CON LANGGRAPH

import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing import TypedDict, List
from datetime import datetime

# Cargar API key
load_dotenv()

# Verificar que existe la API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ ERROR: No se encontró OPENAI_API_KEY en .env")
    print("   Crea el archivo .env con: OPENAI_API_KEY=tu_clave")
    exit(1)

# ============================================
# DEFINIR EL ESTADO COMPARTIDO
# ============================================

class EstadoMedico(TypedDict):
    consulta: str           # Síntomas del paciente
    triage: str             # Clasificación del triage
    diagnostico: str        # Posible diagnóstico
    tratamiento: str        # Recomendación
    historial: List[str]    # Historial de acciones

# ============================================
# AGENTE 1: TRIAGE
# ============================================

def agente_triage(state: EstadoMedico):
    """Agente especializado en clasificar urgencia médica"""
    
    print("   🟡 Agente TRIAGE: Analizando urgencia...")
    
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
    
    prompt = f"""
    Eres un experto en TRIAGE médico. Clasifica estos síntomas:
    
    Síntomas: {state['consulta']}
    
    Responde EXACTAMENTE en este formato:
    COLOR: [ROJO/AMARILLO/VERDE/AZUL]
    JUSTIFICACIÓN: [explicación breve]
    ACCIÓN: [qué hacer inmediatamente]
    """
    
    respuesta = llm.invoke(prompt)
    
    return {
        "triage": respuesta.content,
        "historial": [f"✅ TRIAGE completado - {datetime.now().strftime('%H:%M:%S')}"]
    }

# ============================================
# AGENTE 2: DIAGNÓSTICO
# ============================================

def agente_diagnostico(state: EstadoMedico):
    """Agente especializado en diagnóstico"""
    
    print("   🔵 Agente DIAGNÓSTICO: Evaluando condiciones...")
    
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
    
    prompt = f"""
    Eres un médico diagnosticador. Basado en:
    
    Síntomas: {state['consulta']}
    Triage: {state.get('triage', 'No disponible')}
    
    Proporciona:
    1. POSIBLE DIAGNÓSTICO: (principal sospecha)
    2. DIAGNÓSTICOS DIFERENCIALES: (otras 2 opciones)
    3. CONFIANZA: (Alta/Media/Baja)
    
    Sé conciso y profesional.
    """
    
    respuesta = llm.invoke(prompt)
    
    return {
        "diagnostico": respuesta.content,
        "historial": [f"✅ DIAGNÓSTICO completado - {datetime.now().strftime('%H:%M:%S')}"]
    }

# ============================================
# AGENTE 3: TRATAMIENTO
# ============================================

def agente_tratamiento(state: EstadoMedico):
    """Agente especializado en recomendaciones"""
    
    print("   🟢 Agente TRATAMIENTO: Generando recomendaciones...")
    
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
    
    prompt = f"""
    Eres un especialista en tratamiento médico. Basado en:
    
    Síntomas: {state['consulta']}
    Diagnóstico: {state.get('diagnostico', 'No disponible')}
    
    Recomienda:
    1. ACCIÓN INMEDIATA: (primeros pasos)
    2. TRATAMIENTO SUGERIDO: (medidas generales)
    3. SEÑALES DE ALARMA: (cuándo ir a urgencias)
    4. SEGUIMIENTO: (próximos pasos)
    
    Prioriza siempre la seguridad.
    """
    
    respuesta = llm.invoke(prompt)
    
    return {
        "tratamiento": respuesta.content,
        "historial": [f"✅ TRATAMIENTO completado - {datetime.now().strftime('%H:%M:%S')}"]
    }

# ============================================
# CONSTRUIR EL GRAFO
# ============================================

def construir_sistema_multiagente():
    """Construye el grafo con todos los agentes en cadena"""
    
    # Crear el workflow
    workflow = StateGraph(EstadoMedico)
    
    # Añadir los agentes como nodos
    workflow.add_node("triage", agente_triage)
    workflow.add_node("diagnostico", agente_diagnostico)
    workflow.add_node("tratamiento", agente_tratamiento)
    
    # Definir el flujo (en cadena)
    workflow.set_entry_point("triage")
    workflow.add_edge("triage", "diagnostico")
    workflow.add_edge("diagnostico", "tratamiento")
    workflow.add_edge("tratamiento", END)
    
    # Compilar
    app = workflow.compile()
    
    return app

# ============================================
# FUNCIÓN PRINCIPAL
# ============================================

def consultar_sistema_multiagente(sintomas: str):
    """Función principal para consultar el sistema multiagente"""
    
    print(f"\n{'='*60}")
    print(f"🏥 SISTEMA MULTIAGENTE LANGGRAPH")
    print(f"{'='*60}")
    print(f"\n📝 CONSULTA DEL PACIENTE:")
    print(f"   {sintomas}")
    
    # Construir el sistema
    print(f"\n🤖 INICIANDO AGENTES...")
    print(f"   Los 3 agentes trabajarán en cadena:")
    print(f"   1️⃣ TRIAGE → 2️⃣ DIAGNÓSTICO → 3️⃣ TRATAMIENTO")
    
    sistema = construir_sistema_multiagente()
    
    # Estado inicial
    estado_inicial = {
        "consulta": sintomas,
        "triage": "",
        "diagnostico": "",
        "tratamiento": "",
        "historial": []
    }
    
    # Ejecutar el sistema multiagente
    print(f"\n⚙️ PROCESANDO...\n")
    
    try:
        resultado = sistema.invoke(estado_inicial)
        
        # Mostrar resultados
        print(f"\n{'='*60}")
        print(f"📊 RESULTADOS DEL SISTEMA MULTIAGENTE")
        print(f"{'='*60}")
        
        print(f"\n🔴 AGENTE 1 - TRIAGE:")
        print(f"{'─'*40}")
        print(f"{resultado.get('triage', 'No disponible')}")
        
        print(f"\n🩺 AGENTE 2 - DIAGNÓSTICO:")
        print(f"{'─'*40}")
        print(f"{resultado.get('diagnostico', 'No disponible')}")
        
        print(f"\n💊 AGENTE 3 - TRATAMIENTO:")
        print(f"{'─'*40}")
        print(f"{resultado.get('tratamiento', 'No disponible')}")
        
        print(f"\n📝 HISTORIAL DE ACCIONES:")
        print(f"{'─'*40}")
        for accion in resultado.get('historial', []):
            print(f"   {accion}")
        
        print(f"\n{'='*60}")
        print(f"✅ Consulta completada exitosamente")
        print(f"{'='*60}")
        
        return resultado
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print(f"\nPosibles causas:")
        print(f"   1. API key inválida o sin crédito")
        print(f"   2. Problema de conexión a internet")
        print(f"   3. Formato incorrecto de la API key")
        return None

# ============================================
# PROBAR EL SISTEMA (ejecución directa)
# ============================================

if __name__ == "__main__":
    print("🚀 SISTEMA MULTIAGENTE CON LANGGRAPH")
    print("   Basado en grafos de decisión\n")
    
    # Prueba con un caso simple
    sintomas = input("Describe tus síntomas: ")
    if sintomas:
        consultar_sistema_multiagente(sintomas)