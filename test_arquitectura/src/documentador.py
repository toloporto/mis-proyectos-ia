import os
from crewai import Agent, Task, Crew, LLM

# 1. Conexión nativa a tu modelo local
motor_ia = LLM(
    model="ollama/antolin-dev",
    base_url="http://localhost:11434",
    temperature=0.3
)

# 2. Definimos al Agente Escritor
escritor_tecnico = Agent(
    role='Escritor Técnico Senior',
    goal='Redactar documentación clara y profesional para proyectos de software',
    backstory='Eres un experto creando archivos README.md impecables que explican la arquitectura de un proyecto.',
    llm=motor_ia,
    verbose=True
)

# 3. La Tarea
tarea_readme = Task(
    description='Escribe un breve archivo README.md en español para un proyecto llamado "test_arquitectura". Explica que contiene tres carpetas principales: src/ (para código), datos/ (para archivos locales) y herramientas/ (para utilidades).',
    expected_output='Texto en formato Markdown listo para ser guardado.',
    agent=escritor_tecnico
)

# 4. El Equipo
equipo = Crew(
    agents=[escritor_tecnico],
    tasks=[tarea_readme]
)

print("🚀 El Escritor Técnico está redactando la documentación...")
resultado = equipo.kickoff()

# 5. Guardado seguro del archivo en la raíz del proyecto
# Subimos un nivel desde 'src/' para guardar el README en la carpeta principal
ruta_raiz = os.path.join(os.path.dirname(__file__), '..')
ruta_archivo = os.path.join(ruta_raiz, 'README.md')

with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
    archivo.write(resultado.raw)

print(f"✅ ¡Éxito! Archivo guardado de forma segura en: {ruta_archivo}")