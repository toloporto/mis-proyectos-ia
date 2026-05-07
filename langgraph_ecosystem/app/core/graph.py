from langgraph.graph import StateGraph, END
from app.core.models import load_llm
from app.core.state import AgentState
from app.agents.supervisor import supervisor_node
from app.agents.workers.math_worker import math_worker_node
from app.agents.workers.file_worker import file_worker_node
from langgraph.checkpoint.memory import MemorySaver

# 1. Instanciamos el grafo con nuestro estado personalizado
workflow = StateGraph(AgentState)

# 2. Añadimos los nodos (agentes y herramientas)
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("math_worker", math_worker_node)
workflow.add_node("file_worker", file_worker_node)

# 3. Definimos el punto de entrada
workflow.set_entry_point("supervisor")

# 4. Definimos los condicionales
def router(state: AgentState):
    return state["next_agent"]

workflow.add_conditional_edges(
    "supervisor",
    router,
    {
        "math_worker": "math_worker",
        "file_worker": "file_worker",
        "FINISH": END
    }
)

# 5. Tras ejecutarse, los workers siempre regresan al supervisor
workflow.add_edge("math_worker", "supervisor")
workflow.add_edge("file_worker", "supervisor")

# 6. Compilamos el grafo con checkpointer en memoria
app = workflow.compile(checkpointer=MemorySaver())
