from langchain_core.messages import SystemMessage, HumanMessage
from app.core.state import AgentState
from app.core.models import load_llm
llm = load_llm()

def math_worker_node(state: AgentState):
    """Worker especializado en operaciones matemáticas"""
    last_message = state["messages"][-1].content
    response = llm.invoke([SystemMessage(content="Eres un asistente matemático. Resuelve paso a paso."),
                           HumanMessage(content=last_message)])
    return {"messages": [response]}
