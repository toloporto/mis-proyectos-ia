from crewai import Agent, Task, Crew, Process, LLM

# 1. Usamos la conexión nativa de CrewAI (¡Adiós LangChain!)
# El prefijo 'ollama/' es obligatorio para que sepa dónde buscar
mi_llm = LLM(
    model="ollama/llama3.1",
    base_url="http://localhost:11434"
)

# 2. Definimos al Investigador
investigador = Agent(
    role='Analista Senior de Software',
    goal='Diseñar la lógica para {topic}',
    backstory='Experto en arquitectura de software y seguridad.',
    llm=mi_llm,
    verbose=True,
    allow_delegation=False
)

# 3. Definimos al Programador
programador = Agent(
    role='Desarrollador Senior Python',
    goal='Escribir el código final para {topic}',
    backstory='Maestro del código limpio y PEP8.',
    llm=mi_llm,
    verbose=True,
    allow_delegation=False
)

# 4. Tareas
tarea1 = Task(
    description='Analiza cómo crear un script que organice archivos por extensión.',
    expected_output='Pasos lógicos para el script.',
    agent=investigador
)

tarea2 = Task(
    description='Escribe el código Python basado en el análisis anterior.',
    expected_output='Código Python completo.',
    agent=programador
)

# 5. Equipo
equipo = Crew(
    agents=[investigador, programador],
    tasks=[tarea1, tarea2],
    process=Process.sequential
)

print("🚀 Iniciando equipo multi-agente...")
resultado = equipo.kickoff(inputs={'topic': 'Organizador de Archivos'})
print("\n" + "="*20)
print(resultado)