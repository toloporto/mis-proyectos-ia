from langgraph.graph import StateGraph, MessagesState
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

class BaseMedAgent:
    """Clase base para todos los agentes médicos"""
    
    def __init__(self, model="gpt-3.5-turbo", temperature=0.3):
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.graph = None
    
    def crear_nodo_basico(self, nombre, funcion):
        """Helper para crear grafos simples"""
        builder = StateGraph(MessagesState)
        builder.add_node(nombre, funcion)
        return builder
    
    def invocar(self, mensaje):
        """Método estándar para invocar al agente"""
        if not self.graph:
            raise ValueError("El grafo no ha sido compilado aún")
        return self.graph.invoke({"messages": [("user", mensaje)]})