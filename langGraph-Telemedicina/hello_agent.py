# hello_agent.py - Versión corregida
from langgraph.graph import StateGraph, MessagesState, START, END

# Nodo simple que responde sin llamar a OpenAI
def mi_agente(state: MessagesState):
    """Nodo de prueba que responde sin llamar a OpenAI"""
    # La forma correcta de acceder al mensaje
    ultimo_mensaje = state["messages"][-1]
    contenido_usuario = ultimo_mensaje.content if hasattr(ultimo_mensaje, 'content') else str(ultimo_mensaje)
    
    print(f"📨 Recibido: {contenido_usuario}")
    
    respuesta = "✅ ¡Sistema funcionando! Este agente está listo para procesar consultas de telemedicina."
    
    # Devolvemos el mensaje en el formato correcto
    return {"messages": [("assistant", respuesta)]}

# Construir el grafo
graph_builder = StateGraph(MessagesState)
graph_builder.add_node("agente", mi_agente)
graph_builder.add_edge(START, "agente")
graph_builder.add_edge("agente", END)

# Compilar
app = graph_builder.compile()

# Probar
if __name__ == "__main__":
    print("🚀 Probando LangGraph...")
    print("📝 Creando mensaje de prueba...")
    
    # Invocamos el grafo
    resultado = app.invoke({"messages": [("user", "Hola, quiero verificar mi sistema")]})
    
    # Mostramos la respuesta
    respuesta_final = resultado['messages'][-1]
    contenido_respuesta = respuesta_final.content if hasattr(respuesta_final, 'content') else str(respuesta_final)
    
    print(f"\n💬 Respuesta: {contenido_respuesta}")
    print("\n✅ Todo funciona correctamente!")