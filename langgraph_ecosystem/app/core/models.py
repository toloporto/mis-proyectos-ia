from langchain_ollama import ChatOllama

def load_llm(model_name: str = "qwen2.5:1.5b", base_url: str = "http://localhost:11434"):
    """Carga el modelo LLM local con Ollama"""
    return ChatOllama(
        model=model_name,
        base_url=base_url,
        temperature=0.7,
    )
