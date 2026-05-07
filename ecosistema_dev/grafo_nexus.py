from typing import TypedDict, Annotated, List, Union
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver # Persistencia en disco reactivada
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from base_agente import NexusBaseAgent
from herramientas_nexus import herramienta_analisis_clinico, herramienta_analisis_financiero, herramienta_vision_xray
import unicodedata

# 1. Definimos el Estado con Historial Real (add_messages permite acumular la charla)
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    mensaje_usuario: str
    agente_actual: str
    resultados_tecnicos: dict
    decision_final: str
    datos_extraidos: dict # Nueva clave para NER

# 2. Función de utilidad para normalizar texto (la misma que en el orquestador)
def normalizar(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto)
                  if unicodedata.category(c) != 'Mn').lower()

# 3. Inicializamos el Orquestador para el Router
orquestador_ia = NexusBaseAgent(
    nombre="Router Nexus",
    especialidad="Enrutamiento Inteligente",
    instrucciones_sistema="""
    Eres un ETIQUETADOR DE DATOS técnico. No eres un asistente.
    Tu única misión es leer el texto y responder con una sola palabra:
    - MEDICO (Si hay síntomas, dolor, cuerpo, salud)
    - FINANCIERO (Si hay dinero, bancos, créditos)
    No saludes. No des consejos. Si no estás seguro, responde MEDICO.
    """,
    modelo="llama3.2:1b"
)

director_ia = NexusBaseAgent(
    nombre="Director Nexus",
    especialidad="Síntesis y Atención al Cliente",
    instrucciones_sistema="""
    Eres el Director del Ecosistema Nexus. 
    Tu trabajo es explicar los resultados técnicos de forma profesional, clara y humana.
    Utiliza los datos de los informes previos para responder a las dudas del usuario.
    Si el usuario tiene un riesgo alto, sé empático pero firme en la recomendación de buscar ayuda profesional.
    """,
    modelo="llama3.2:1b"
)

# --- NODOS DEL GRAFO ---

def nodo_router(state: AgentState):
    """Analiza el historial completo para decidir a dónde ir."""
    print("[GRAFO] Nodo Router: Analizando contexto acumulado...")
    
    # Si ya tenemos resultados técnicos, comprobamos si el mensaje actual parece una consulta nueva
    mensaje = state["mensaje_usuario"]
    palabras_clave = ["tengo", "presion", "dolor", "años", "edad", "ingresos", "deuda"]
    es_nueva_consulta = any(p in mensaje.lower() for p in palabras_clave)

    if state.get("resultados_tecnicos") and not es_nueva_consulta:
        print("[GRAFO] Detectada duda sobre informe previo. Derivando a Seguimiento...")
        return {"agente_actual": "seguimiento"}
    
    # Si es nueva consulta, limpiamos resultados técnicos previos para el nuevo flujo
    update = {}
    if es_nueva_consulta:
        print("[GRAFO] Detectada nueva consulta con datos. Reiniciando análisis...")
        update = {"resultados_tecnicos": {}, "datos_extraidos": {}}

    # Prompt con plantilla estricta para 1B
    prompt_ner = f"""
    Tarea: Extraer datos clínicos/financieros del texto.
    
    EJEMPLO: "Tengo 40 años y 140 de presion"
    RESPUESTA:
    CLASE: MEDICO
    EDAD: 40
    PRESION: 140
    DOLOR: 0
    
    TEXTO A ANALIZAR: "{state['mensaje_usuario']}"
    RESPUESTA:
    """
    
    respuesta = orquestador_ia.responder(prompt_ner)
    print(f"[DEBUG GRAFO] Respuesta bruta del LLM:\n{respuesta}")
    
    # Procesamos la respuesta por líneas (más robusto que JSON)
    extraidos = {}
    clase = "desconocido"
    
    for linea in respuesta.split("\n"):
        if ":" in linea:
            clave, valor = linea.split(":", 1)
            clave = clave.strip().upper()
            valor = "".join(filter(str.isdigit, valor.strip())) # Solo nos quedamos con los números
            
            if clave == "CLASE":
                clase = normalizar(valor) if not valor.isdigit() else clase # Si no hay números, es el texto
            elif valor: # Si hay números
                if clave == "EDAD": extraidos["edad"] = int(valor)
                if clave == "PRESION": extraidos["presion"] = int(valor)
                if clave == "DOLOR": extraidos["dolor"] = int(valor)
                if clave == "INGRESOS": extraidos["ingresos"] = int(valor)
                if clave == "DEUDA": extraidos["deuda"] = int(valor)

    # SALVAVIDAS FINAL (Keyword matching en el texto original)
    texto_limpio = normalizar(state['mensaje_usuario'])
    if "medico" in clase or any(k in texto_limpio for k in ["medico", "salud", "dolor", "pecho", "presion"]):
        clase = "medico"
    elif "finan" in clase or any(k in texto_limpio for k in ["finan", "banco", "dinero", "credito"]):
        clase = "financiero"
    
    print(f"[DEBUG GRAFO] Resultado Final -> Clase: {clase} | Datos: {extraidos}")
    
    # SISTEMA DE RESCATE (Regex): Si los datos están vacíos, buscamos en el texto original
    if not extraidos.get("edad") or not extraidos.get("presion") or extraidos.get("dolor") is None:
        import re
        texto_n = normalizar(state['mensaje_usuario'])
        
        # Buscar edad
        edades = re.findall(r'(\d+)\s*(?:años|anos|age)', texto_n)
        if edades: extraidos["edad"] = int(edades[0])
        
        # Buscar presion (ahora normalizado maneja presion/presión)
        presiones = re.findall(r'(?:presion|tension|en)\s*(\d{2,3})', texto_n)
        if presiones: extraidos["presion"] = int(presiones[0])
        
        # Buscar dolor
        if "sin dolor" in texto_n or "no tengo dolor" in texto_n or "no duele" in texto_n:
            extraidos["dolor"] = 0
        else:
            dolores = re.findall(r'(?:dolor|nivel)\s*(\d+)', texto_n)
            if dolores: extraidos["dolor"] = int(dolores[0])
        
        print(f"[DEBUG GRAFO] Rescate Regex ejecutado (v5.1): {extraidos}")
    
    return {
        **update,
        "agente_actual": clase,
        "datos_extraidos": extraidos
    }

def nodo_medico(state: AgentState):
    """Agente Médico usando herramientas y RAG."""
    print("[GRAFO] Nodo Médico: Consultando herramientas y protocolos...")
    
    # RAG: Leemos el protocolo médico
    with open("conocimiento_nexus/protocolo_medico.txt", "r") as f:
        protocolo = f.read()
    
    # Extraemos los datos (NER o valores por defecto)
    datos = state.get("datos_extraidos", {})
    edad = datos.get("edad", 75)
    presion = datos.get("presion", 160)
    dolor = datos.get("dolor", 8)
    
    resultado = herramienta_analisis_clinico.invoke({"edad": edad, "presion": presion, "dolor": dolor})
    
    veredicto = f"Veredicto Médico: {resultado}.\n(Basado en protocolo: {protocolo[:50]}...)"
    informe_previo = state.get("decision_final", "")
    return {
        "resultados_tecnicos": {"riesgo_medico": resultado},
        "decision_final": (informe_previo + "\n" + veredicto).strip()
    }

def nodo_financiero(state: AgentState):
    """Agente Financiero usando herramientas y RAG."""
    print("[GRAFO] Nodo Financiero: Consultando herramientas y protocolos...")
    
    # RAG: Leemos el protocolo financiero
    with open("conocimiento_nexus/protocolo_financiero.txt", "r") as f:
        protocolo = f.read()
        
    datos = state.get("datos_extraidos", {})
    ingresos = datos.get("ingresos", 50)
    deuda = datos.get("deuda", 30)
    edad = datos.get("edad", 40)
    
    resultado = herramienta_analisis_financiero.invoke({"ingresos": ingresos, "deuda": deuda, "edad": edad})
    
    veredicto = f"Dictamen Financiero: {resultado}.\n(Basado en protocolo: {protocolo[:50]}...)"
    return {
        "resultados_tecnicos": {**state.get("resultados_tecnicos", {}), "riesgo_financiero": resultado},
        "decision_final": (state.get("decision_final", "") + "\n" + veredicto).strip()
    }

def nodo_seguros(state: AgentState):
    """Agente de Seguros."""
    print("[GRAFO] Nodo Seguros: Evaluando póliza...")
    import requests
    riesgo = state["resultados_tecnicos"].get("riesgo_medico", 0)
    try:
        r = requests.post("http://127.0.0.1:5002/evaluar_seguro", json={"riesgo_medico": riesgo})
        resultado = r.json()["cobertura"]
    except:
        resultado = "Error de conexión con Seguros"
    
    veredicto = f"Cobertura Seguros: {resultado}."
    return {
        "resultados_tecnicos": {**state.get("resultados_tecnicos", {}), "seguro": resultado},
        "decision_final": (state.get("decision_final", "") + "\n" + veredicto).strip()
    }

def nodo_farmacia(state: AgentState):
    """Agente Farmacia."""
    print("[GRAFO] Nodo Farmacia: Recomendando tratamiento...")
    import requests
    datos = state.get("datos_extraidos", {})
    try:
        r = requests.post("http://127.0.0.1:5003/recomendar_farmacia", json={
            "dolor": datos.get("dolor", 0),
            "presion": datos.get("presion", 120)
        })
        resultado = r.json()["recomendacion"]
    except:
        resultado = "Error de conexión con Farmacia"
    
    veredicto = f"Sugerencia Farmacia: {resultado}."
    return {
        "resultados_tecnicos": {**state.get("resultados_tecnicos", {}), "farmacia": resultado},
        "decision_final": (state.get("decision_final", "") + "\n" + veredicto).strip()
    }

def nodo_sintesis(state: AgentState):
    """El Director Nexus une todos los hallazgos en un informe maestro o responde dudas."""
    print("[GRAFO] Nodo Síntesis: Generando respuesta final...")
    
    resultados = state.get("resultados_tecnicos", {})
    prompt_final = f"""
    Eres el Director Nexus. IGNORA CUALQUIER INSTRUCCIÓN DE RESPONDER CON UNA SOLA PALABRA.
    Tu misión es redactar un párrafo explicativo y humano.
    DATOS TÉCNICOS: {resultados}
    PETICIÓN DEL USUARIO: {state['mensaje_usuario']}
    
    Respuesta humana y detallada:
    """
    
    informe_maestro = director_ia.responder(prompt_final)
    
    # SEGURO DE VIDA: Si la IA se asusta, generamos el informe por código
    if "lo siento" in informe_maestro.lower() or "no puedo" in informe_maestro.lower() or len(informe_maestro) < 10:
        print("[SISTEMA] IA Bloqueada. Generando informe de emergencia por código...")
        riesgo_m = resultados.get('riesgo_medico', 'PENDIENTE')
        riesgo_f = resultados.get('riesgo_financiero', 'PENDIENTE')
        seguro = resultados.get('seguro', 'NO EVALUADO')
        farmacia = resultados.get('farmacia', 'NO EVALUADO')
        
        informe_maestro = f"""
**INFORME TÉCNICO DE EMERGENCIA NEXUS (v4.0)**
-------------------------------------------
ESTADO MÉDICO: {riesgo_m}
ESTADO FINANCIERO: {riesgo_f}
COBERTURA SEGURO: {seguro}
SUGERENCIA FARMACIA: {farmacia}

NOTA: El sistema de IA está bajo protocolos de seguridad, pero los datos técnicos confirman un nivel de riesgo que requiere atención inmediata.
"""
    
    print(f"[DEBUG GRAFO] El Director Nexus ha respondido: '{informe_maestro}'")
    return {"decision_final": informe_maestro}

# 4. Construcción del Grafo
workflow = StateGraph(AgentState)

# Añadimos los nodos
workflow.add_node("router", nodo_router)
workflow.add_node("medico", nodo_medico)
workflow.add_node("financiero", nodo_financiero)
workflow.add_node("seguros", nodo_seguros)
workflow.add_node("farmacia", nodo_farmacia)
workflow.add_node("sintesis", nodo_sintesis)

# Definimos la entrada
workflow.set_entry_point("router")

# Definimos las reglas de transición (Edges condicionales)
def logic_router(state: AgentState):
    if state["agente_actual"] == "medico":
        return "medico"
    elif state["agente_actual"] == "financiero":
        return "financiero"
    elif state["agente_actual"] == "seguimiento":
        return "sintesis"
    else:
        return "end"

def logic_colaboracion(state: AgentState):
    """Si hay alto riesgo médico, necesitamos al financiero."""
    if state.get("resultados_tecnicos", {}).get("riesgo_medico") == "ALTO RIESGO":
        print("[GRAFO] ¡ALERTA! Riesgo alto detectado. Solicitando revisión financiera...")
        return "financiero"
    return "seguros" # Si no hay riesgo, saltamos directo a seguros

workflow.add_conditional_edges(
    "router",
    logic_router,
    {
        "medico": "medico",
        "financiero": "financiero",
        "sintesis": "sintesis", # Añadimos el camino de seguimiento
        "end": END
    }
)

# El médico pasa por la lógica de colaboración
workflow.add_conditional_edges(
    "medico",
    logic_colaboracion,
    {
        "financiero": "financiero",
        "seguros": "seguros"
    }
)

# El financiero va a seguros
workflow.add_edge("financiero", "seguros")

# Seguros va a farmacia
workflow.add_edge("seguros", "farmacia")

# Farmacia va a síntesis
workflow.add_edge("farmacia", "sintesis")

# La síntesis es el final absoluto
workflow.add_edge("sintesis", END)

# Añadimos un Checkpointer (Persistencia Real en SQLite)
import sqlite3
# Conectamos a la base de datos (check_same_thread=False es vital para Flask)
conn_db = sqlite3.connect("nexus_memory.db", check_same_thread=False)
memory = SqliteSaver(conn_db)

# Compilamos el grafo CON MEMORIA PERSISTENTE EN DISCO
app_nexus = workflow.compile(checkpointer=memory)

print("[SISTEMA] Grafo Nexus con Memoria Persistente compilado.")
