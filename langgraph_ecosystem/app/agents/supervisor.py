from langchain_core.messages import SystemMessage, HumanMessage
from app.core.state import AgentState
from app.core.models import load_llm

llm = load_llm()

def supervisor_node(state: AgentState):
    """Nodo supervisor: decide qué worker ejecutar o si finalizar"""
    last_message = state["messages"][-1].content if state["messages"] else ""
    
    # Prompt simple para decidir (en producción usarías structured output)
    decision_prompt = f"""
    Eres un supervisor. Basado en la entrada del usuario, decide:
    - Si es una operación matemática (suma, resta, etc.) responde solo "math_worker"
    - Si es sobre archivos (leer, guardar) responde solo "file_worker"
    - Si es un saludo o conversación general, responde "FINISH"
    
    Entrada: {last_message}
    """
    
    decision = llm.invoke([SystemMessage(content=decision_prompt)]).content.strip().lower()
    
    # Limpiar posible código markdown o comillas
    if "math_worker" in decision:
        next_agent = "math_worker"
    elif "file_worker" in decision:
        next_agent = "file_worker"
    else:
        next_agent = "FINISH"
    
    return {
        "next_agent": next_agent,
        "iteration_count": state.get("iteration_count", 0) + 1
    }
