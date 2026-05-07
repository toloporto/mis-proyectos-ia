from langchain_core.tools import tool
from typing import Dict, Any, Callable
from .code_interpreter import execute_python_code

# TODO: Integración MCP. Para un entorno avanzado, aquí leeríamos dinámicamente
# los servidores MCP configurados y los transformaríamos en herramientas de LangChain.

@tool
def web_search_tool(query: str) -> str:
    """Busca en internet utilizando un buscador local o externo."""
    # Simulación para el ejemplo
    return f"Resultados de búsqueda en la web para: {query}"

@tool
def run_python_code(code: str) -> str:
    """
    Ejecuta un script de Python y devuelve la salida (stdout) y los errores (stderr).
    Usa esta herramienta cuando necesites calcular algo, procesar datos o graficar.
    """
    return execute_python_code(code)

# Registro global
AVAILABLE_TOOLS = {
    "web_search": web_search_tool,
    "run_python": run_python_code
}

def get_tools_for_agent(enabled_tools_keys: list[str]) -> list[Callable]:
    """
    Convierte la lista de strings (claves) guardada en BD
    en una lista de objetos Tool de LangChain.
    """
    tools = []
    for key in enabled_tools_keys:
        if key in AVAILABLE_TOOLS:
            tools.append(AVAILABLE_TOOLS[key])
    return tools
