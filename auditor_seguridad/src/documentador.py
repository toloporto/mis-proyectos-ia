import os
from crewai import Agent, Task, Crew, LLM

# 1. Configurar el motor
motor_ia = LLM(
    model="ollama/llama3.1",
    base_url="http://localhost:11434",
    temperature=0.3
)

# 2. El Agente Escritor
escritor = Agent(
    role='Escritor Técnico Senior',
    goal='Crear un archivo README.md claro y profesional para el Auditor de Seguridad',
    backstory='Eres un experto redactando manuales para herramientas de ciberseguridad hechas en Python.',
    llm=motor_ia,
    verbose=True
)

# 3. La Tarea
tarea_readme = Task(
    description='Escribe un archivo README.md en español para el proyecto "auditor_seguridad". Explica brevemente que es un sistema automatizado con CrewAI que lee archivos de log locales para detectar ataques de fuerza bruta y bloquear IPs maliciosas.',
    expected_output='Texto en formato Markdown listo para ser guardado.',
    agent=escritor
)

# 4. Ejecución
equipo = Crew(agents=[escritor], tasks=[tarea_readme])
print("✍️ Redactando la documentación del proyecto...")
resultado = equipo.kickoff()

# 5. Guardado seguro en la raíz
ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ruta_readme = os.path.join(ruta_raiz, 'README.md')

with open(ruta_readme, 'w', encoding='utf-8') as archivo:
    archivo.write(resultado.raw)

print(f"\n✅ README.md guardado con éxito en: {ruta_readme}")