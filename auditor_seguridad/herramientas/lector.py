from crewai.tools import tool

@tool("Leer Log")
def leer_log(ruta_archivo: str) -> str:
    """
    Abre y lee un archivo de registro (log) local. 
    Útil para buscar errores de seguridad o ataques.
    """
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error al leer el archivo: {e}"