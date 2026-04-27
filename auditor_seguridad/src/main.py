import os
import sys

# 1. Truco de Arquitecto: Que Python vea la carpeta de herramientas
ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ruta_raiz)

from crewai import Agent, Task, Crew, LLM
from herramientas.lector import leer_log

# 2. Configurar Llama 3.1 (el cerebro experto en herramientas)
motor_ia = LLM(
    model="ollama/llama3.1",
    base_url="http://localhost:11434",
    temperature=0.2
)

# 3. Nuestro Agente Auditor
auditor = Agent(
    role='Auditor de Seguridad Senior',
    goal='Analizar registros (logs) en busca de amenazas y resumirlas claramente.',
    backstory='Eres un experto en ciberseguridad. Tu tarea es encontrar ataques de fuerza bruta y advertir sobre IPs maliciosas.',
    llm=motor_ia,
    tools=[leer_log],
    verbose=True,
    max_iter=3
)

# 4. La Tarea (Definimos la ruta absoluta usando la ruta_raiz que calculamos arriba)
ruta_del_log = os.path.join(ruta_raiz, 'datos', 'registro_servidor.log')

tarea_analisis = Task(
    description=f'''
    PASO 1: Ejecuta la herramienta "Leer Log" pasándole exactamente esta ruta: {ruta_del_log}
    PASO 2: Analiza el texto devuelto.
    PASO 3: Redacta y devuelve inmediatamente un informe de seguridad en ESPAÑOL y en TEXTO PLANO. 
    NO uses formato JSON. NO uses herramientas más de una vez.
    ''',
    expected_output='Un reporte en español indicando el tipo de ataque y la IP maliciosa.',
    agent=auditor
)

# 5. Ejecutar la IA
equipo = Crew(agents=[auditor], tasks=[tarea_analisis])

print("🛡️ Iniciando Auditoría de Seguridad...\n")
resultado = equipo.kickoff()

print("\n" + "="*40)
print("🚨 INFORME DE SEGURIDAD GENERADO:")
print("="*40)
print(resultado)