try:
    from langgraph.graph import Graph, END
    from langchain_ollama import OllamaLLM
    from pydantic import BaseModel
    from typing import Dict
    
    llm = OllamaLLM(model="llama3.2:1b", base_url="http://localhost:11434")
    
    class Estado(BaseModel):
        input: str
        output: str = ""
    
    def agente_ortodoncia(state: dict) -> Dict:
        prompt = f"Ortodoncia: {state.get('input', '')}. Análisis y plan breve."
        try:
            resp = llm.invoke(prompt)
            return {"output": resp}
        except Exception as e:
            return {"output": f"Error LLM: {str(e)}"}
    
    graph = Graph()
    graph.add_node("agente", agente_ortodoncia)
    graph.set_entry_point("agente")
    graph.add_edge("agente", END)
    ortodoncia_agent = graph.compile()
    
    print("✅ Agente cargado OK")
except Exception as e:
    print(f"❌ Error carga agente: {e}")
    ortodoncia_agent = None
