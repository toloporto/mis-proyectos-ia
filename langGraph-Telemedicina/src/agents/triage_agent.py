from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

def triage_medico(state: MessagesState):
    """Clasifica la urgencia de una consulta médica"""
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
    consulta = state["messages"][-1].content
    
    prompt = f"""
    Eres un sistema de triage médico. Clasifica URGENTEMENTE esta consulta en:
    - 'ROJO' (vida en peligro, requiere acción inmediata)
    - 'AMARILLO' (condición seria, atención en <30min)  
    - 'VERDE' (menor urgencia, puede esperar)
    - 'AZUL' (consulta administrativa o informativa)
    
    Consulta: {consulta}
    
    Responde SOLO con: [COLOR] - [RAZÓN BREVE]
    """
    
    respuesta = llm.invoke(prompt)
    return {"messages": [("assistant", respuesta.content)]}

# Construir el grafo
builder = StateGraph(MessagesState)
builder.add_node("triage", triage_medico)
builder.add_edge(START, "triage")
builder.add_edge("triage", END)
triage_app = builder.compile()