import subprocess
import tempfile
import os

def execute_python_code(code: str) -> str:
    """
    Ejecuta código Python de manera controlada.
    CUIDADO: En un entorno de producción real, esto DEBE correr dentro de un 
    contenedor Docker seguro (sandbox) o usar herramientas como E2B.
    Para este entorno local dev, lo ejecutaremos usando subprocess en un archivo temporal.
    """
    # Guardamos el código en un archivo temporal
    fd, temp_path = tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(code)
            
        # Ejecutamos con un timeout de 10 segundos
        result = subprocess.run(
            ["python", temp_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\nErrores:\n{result.stderr}"
            
        return output
    except subprocess.TimeoutExpired:
        return "Error: Timeout. El código tardó más de 10 segundos en ejecutarse."
    except Exception as e:
        return f"Error inesperado ejecutando el código: {str(e)}"
    finally:
        # Limpieza
        if os.path.exists(temp_path):
            os.remove(temp_path)
