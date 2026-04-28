from crewai.tools import tool
from duckduckgo_search import DDGS

@tool("Investigar IP en Internet")
def investigar_ip(ip: str) -> str:
    """
    Busca información sobre la reputación y origen de una dirección IP en la web.
    Útil para saber si una IP detectada en los logs pertenece a una botnet o es maliciosa.
    """
    try:
        with DDGS() as ddgs:
            # Buscamos la IP en sitios de reputación
            query = f"reputation and threat info for IP {ip}"
            results = [r for r in ddgs.text(query, max_results=3)]
            
            if not results:
                return f"No se encontró información pública sobre la IP {ip}."
            
            # Formateamos el resultado para el agente
            respuesta = f"Resultados de investigación para {ip}:\n"
            for r in results:
                respuesta += f"- {r['title']}: {r['body']}\n"
            return respuesta
    except Exception as e:
        return f"Error al investigar la IP: {str(e)}"