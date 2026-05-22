import os
import subprocess

def crear_estructura_proyecto(nombre_proyecto):
    """
    Genera la estructura de carpetas estándar y el entorno virtual
    para un nuevo proyecto de Inteligencia Artificial.
    """
    # 1. Definir la ruta base localmente
    ruta_base = os.path.join(os.getcwd(), 'proyectos', nombre_proyecto)

    if os.path.exists(ruta_base):
        print(f"❌ Error: La carpeta '{nombre_proyecto}' ya existe.")
        return

    # 2. Crear carpetas de la arquitectura
    carpetas = ['src', 'datos', 'herramientas']
    for carpeta in carpetas:
        os.makedirs(os.path.join(ruta_base, carpeta))
        print(f"📁 Creada carpeta: {carpeta}/")

    # 3. Crear un archivo principal (main.py) básico
    archivo_main = os.path.join(ruta_base, 'src', 'main.py')
    with open(archivo_main, 'w') as f:
        f.write('print("¡Proyecto inicializado y listo para codificar!")\n')
    
    print("✅ Archivo base creado: src/main.py")

    # 4. Construir el entorno virtual de forma automática
    print("⚙️ Construyendo el entorno aislado (.venv)... esto tardará unos segundos.")
    subprocess.run(["python", "-m", "venv", os.path.join(ruta_base, '.venv')])

    # 5. Instrucciones finales
    print("\n" + "="*40)
    print("🎉 ¡NUEVO PROYECTO CREADO CON ÉXITO! 🎉")
    print("="*40)
    print("Sigue estos dos pasos para empezar a trabajar:")
    print(f"1. Entra a la carpeta:  cd proyectos/{nombre_proyecto}")
    print("2. Activa tu entorno:   .\\.venv\\Scripts\\activate")
    print("="*40 + "\n")

# --- Ejecución del programa ---
if __name__ == "__main__":
    nuevo_nombre = input("🚀 Introduce el nombre de tu nuevo proyecto (ej. asistente_voz): ")
    # Convertimos espacios a guiones bajos para mantener nombres limpios
    nuevo_nombre_limpio = nuevo_nombre.strip().replace(" ", "_")
    crear_estructura_proyecto(nuevo_nombre_limpio)