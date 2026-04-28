import hashlib
from crewai.tools import tool

@tool("Analizar Archivo Sospechoso")
def analizar_archivo(ruta_archivo: str) -> str:
    """
    Calcula la huella digital (SHA-256) de un archivo sospechoso.
    Útil para identificar malware sin llegar a ejecutar el archivo.
    """
    try:
        sha256_hash = hashlib.sha256()
        with open(ruta_archivo, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        huella = sha256_hash.hexdigest()
        return f"El archivo tiene la huella SHA-256: {huella}. Es una huella única para identificar virus conocidos."
    except Exception as e:
        return f"Error al analizar el archivo: {str(e)}"