from langgraph.graph import StateGraph, MessagesState, START, END
import sys
sys.path.append('..')
from agents.triage_agent import triage_medico

def workflow_atencion_completa(state: MessagesState):
    """Flujo completo: triage → diagnóstico → recomendación"""
    
    # Paso 1: Triage
    resultado_triage = triage_medico(state)
    
    # Aquí irían más pasos (por ahora es un placeholder)
    return {"messages": resultado_triage["messages"]}

# Construir workflow
builder = StateGraph(MessagesState)
builder.add_node("triage", triage_medico)
builder.add_edge(START, "triage")
builder.add_edge("triage", END)
workflow = builder.compile()