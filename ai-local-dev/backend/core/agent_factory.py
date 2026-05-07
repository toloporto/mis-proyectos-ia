from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama
# TODO: Claude implementation when needed
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# Dependencias locales
from .models import AgentConfiguration

# Definición del Estado del Agente
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    agent_id: int
    context: str

import os

def get_llm(config: AgentConfiguration):
    """Devuelve la instancia del LLM basado en la configuración."""
    if config.llm_model.startswith("gemini"):
        # Evitar conflicto con Google Cloud
        os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
        # Recuperar API KEY del entorno o usar una por defecto (la misma de test.py)
        api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyDBU-X__S1GJYuoOBMggUzBILyotIuTBfU")
        return ChatGoogleGenerativeAI(
            model=config.llm_model, 
            temperature=config.temperature,
            google_api_key=api_key
        )
    elif config.llm_model.startswith("ollama:"):
        model_name = config.llm_model.split(":")[1]
        return ChatOllama(model=model_name, temperature=config.temperature)
    else:
        # Fallback o genérico
        return ChatOllama(model="llama3.2:1b", temperature=config.temperature)

def create_agent_graph(config: AgentConfiguration):
    """Crea y devuelve un grafo LangGraph compilado para el agente."""
    
    llm = get_llm(config)
    
    # Nodo principal del agente
    def agent_node(state: AgentState):
        messages = state["messages"]
        
        # Inyectar System Prompt como primer mensaje si no está
        # o procesarlo junto con los mensajes
        system_msg = [("system", config.system_prompt)]
        
        if config.use_rag and state.get("context"):
            system_msg[0] = ("system", config.system_prompt + "\n\nContexto extraído:\n" + state["context"])
            
        # Invocar LLM
        response = llm.invoke(system_msg + [(msg.type, msg.content) for msg in messages])
        return {"messages": [response]}
        
    # TODO: Nodo de RAG (recuperación)
    def rag_node(state: AgentState):
        # Aquí llamaríamos a Qdrant
        return {"context": "Contexto simulado desde Qdrant..."}

    workflow = StateGraph(AgentState)
    
    # Agregar nodos
    workflow.add_node("agent", agent_node)
    
    if config.use_rag:
        workflow.add_node("retrieve", rag_node)
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "agent")
    else:
        workflow.set_entry_point("agent")
        
    # TODO: Agregar nodo de Code Interpreter si config.has_code_interpreter es True
        
    workflow.add_edge("agent", END)
    
    return workflow.compile()
