import os
import sys

# 1. Truco de Arquitecto: Que Python vea la carpeta de herramientas
ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ruta_raiz)

from crewai import Agent, Task, Crew, LLM
from herramientas.lector import leer_log
from herramientas.notificador import enviar_alerta 
from herramientas.buscador import investigar_ip
from herramientas.analizador_archivos import analizar_archivo 

# 2. Configurar Llama 3.1 
motor_ia = LLM(
    model="ollama/llama3.1",
    base_url="http://localhost:11434",
    temperature=0.0
)

# 3. Nuestro Agente Auditor
auditor = Agent(
    role='Auditor de Seguridad Senior e Investigador de Amenazas',
    goal='Analizar registros, investigar amenazas híbridas (IPs y archivos) y alertar al sistema.',
    backstory='Eres un experto en ciberseguridad. Tu tarea es analizar logs, usar inteligencia global para investigar atacantes, verificar firmas de archivos sospechosos y emitir alertas críticas.',
    llm=motor_ia,
    tools=[leer_log, investigar_ip, analizar_archivo, enviar_alerta],
    verbose=True,
    max_iter=10
)

# 4. La Tarea DEFINITIVA (Fusionada y limpia)
ruta_del_log = os.path.join(ruta_raiz, 'datos', 'registro_servidor.log')

tarea_definitiva = Task(
    description=f'''
    PASO 1: Usa "Leer Log" en {ruta_del_log}.
    PASO 2: Es OBLIGATORIO usar "Investigar IP en Internet" para la IP 185.220.101.44 antes de seguir.
    PASO 3: Es OBLIGATORIO usar "Analizar Archivo Sospechoso" para la ruta del virus mencionada en el log.
    PASO 4: Una vez tengas los resultados de ambos análisis, usa "Enviar Alerta de Seguridad".
    PASO 5: Redacta el informe final detallando qué decía internet de la IP y cuál es el hash del archivo.
    ''',
    expected_output='Informe detallado con IP, Hash del archivo y confirmación de alerta.',
    agent=auditor
)

# 5. Ejecutar la IA
equipo = Crew(agents=[auditor], tasks=[tarea_definitiva])

print("🛡️ Iniciando Auditoría de Seguridad Híbrida...\n")
resultado = equipo.kickoff()

print("\n" + "="*40)
print("🚨 INFORME DE SEGURIDAD GENERADO:")
print("="*40)
print(resultado)