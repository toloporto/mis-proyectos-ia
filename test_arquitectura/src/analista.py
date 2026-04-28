import os
import sys

# --- EL TRUCO DEL ARQUITECTO ---
# Le decimos a Python que añada la carpeta raíz a su "radar" de búsqueda
ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ruta_raiz)
# -------------------------------

from crewai import Agent, Task, Crew, LLM
# Ahora Python ya sabe dónde está la carpeta 'herramientas'
from herramientas.mis_herramientas import leer_archivo

# 1. Configuración del motor local
motor_ia = LLM(
    model="ollama/llama3.1",
    base_url="http://localhost:11434",
    temperature=0.2
)

# 2. Definición del Agente con su "Skill"
analista_seguridad = Agent(
    role='Analista de Ciberseguridad',
    goal='Examinar archivos de log para identificar riesgos de seguridad',
    backstory='Experto forense de sistemas. Tu especialidad es encontrar patrones de error en archivos de texto plano.',
    llm=motor_ia,
    tools=[leer_archivo],
    verbose=True
)

# 3. Definición de la Tarea con ruta absoluta
ruta_log = '/home/toloporto/proyectos/test_arquitectura/datos/reporte_sistema.txt'

tarea_diagnostico = Task(
    description=f'Usa la herramienta Lector de Archivos para analizar el documento en {ruta_log}. Identifica el error más grave.',
    expected_output='Un informe técnico con el error detectado y una posible solución.',
    agent=analista_seguridad
)

# 4. Orquestación
equipo = Crew(
    agents=[analista_seguridad],
    tasks=[tarea_diagnostico]
)

print("🔍 El Analista está examinando el archivo de datos...")
resultado = equipo.kickoff()

print("\n" + "="*30)
print("📄 DIAGNÓSTICO FINAL:")
print("="*30 + "\n")
print(resultado)