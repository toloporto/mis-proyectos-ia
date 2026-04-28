from crewai.tools import tool
import os

@tool("Lector de Archivos")
def leer_archivo(ruta_archivo: str) -> str:
    """
    Lee el contenido de un archivo de texto y lo devuelve.
    Útil para analizar logs, código o documentos de datos.
    """
    try:
        # Priorizamos 'with open' por seguridad, tal y como dictan tus reglas
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"❌ Error al leer el archivo: {e}"