# src/agents/prompts.py
"""Módulo de prompts clínicos estructurados para el Sistema Multiagente Médico.
Centraliza todas las plantillas de prompts para facilitar iteración y mejora.
"""

from typing import Optional


def prompt_triage(sintomas: str, edad: Optional[int] = None, nombre: Optional[str] = None) -> str:
    """Prompt estructurado para el agente de triage"""
    contexto = ""
    if edad and edad > 0:
        contexto += f"- Edad del paciente: {edad} años\n"
    if nombre:
        contexto += f"- Nombre: {nombre}\n"

    return f"""Eres un médico de urgencias con 20 años de experiencia clínica.

DATOS DE LA CONSULTA:
- Síntomas reportados: {sintomas}
{contexto}
INSTRUCCIÓN: Evalúa el nivel de urgencia médica de forma objetiva.

RESPONDE EXACTAMENTE en este formato (sin texto adicional antes o después):
NIVEL: [escribe solo una: LEVE | MODERADO | GRAVE | EMERGENCIA]
RAZÓN: [una frase explicando el nivel asignado]
ALERTA: [síntoma específico que requeriría escalar a mayor urgencia]"""


def prompt_diagnostico(sintomas: str, edad: Optional[int] = None) -> str:
    """Prompt estructurado para el agente de diagnóstico"""
    contexto = f" en paciente de {edad} años" if edad and edad > 0 else ""

    return f"""Eres un médico internista especializado en diagnóstico clínico diferencial.

SÍNTOMAS{contexto}: {sintomas}

INSTRUCCIÓN: Proporciona un diagnóstico diferencial conciso y clínicamente relevante.

RESPONDE en este formato:
DIAGNÓSTICO_PRINCIPAL: [condición más probable, en términos médicos claros]
DIFERENCIAL: [1-2 condiciones alternativas a descartar]
EXÁMENES_CLAVE: [prueba o pruebas que confirmarían el diagnóstico]"""


def prompt_tratamiento(
    sintomas: str,
    nivel_urgencia: str = "MODERADO",
    edad: Optional[int] = None
) -> str:
    """Prompt estructurado para el agente de tratamiento"""
    contexto = f" para paciente de {edad} años" if edad and edad > 0 else ""

    return f"""Eres un médico clínico con experiencia en urgencias y atención primaria.

SÍNTOMAS{contexto}: {sintomas}
NIVEL DE URGENCIA: {nivel_urgencia}

INSTRUCCIÓN: Proporciona recomendaciones de tratamiento acordes al nivel de urgencia.

RESPONDE en este formato:
ACCIÓN_INMEDIATA: [qué hacer en las próximas 1-2 horas]
MEDICACIÓN: [si corresponde: fármaco, dosis y frecuencia — si no: "Consultar médico"]
SEGUIMIENTO: [cuándo y cómo hacer seguimiento]
ALARMA: [síntomas que indicarían necesidad de acudir a urgencias]"""


def prompt_emergencia(sintomas: str) -> str:
    """Respuesta de protocolo de emergencia (sin pasar por LLM completo)"""
    return (
        f"🚨 EMERGENCIA MÉDICA — Los síntomas descritos ({sintomas[:120]}...) "
        "requieren atención médica INMEDIATA.\n\n"
        "▶ LLAMA AL 112 ahora o acude a urgencias hospitalarias.\n"
        "▶ No conduzcas tú mismo/a si te sientes inestable.\n"
        "▶ Informa a alguien de tu entorno de tu situación.\n\n"
        "No esperes a que los síntomas mejoren solos. En una emergencia, cada minuto cuenta."
    )


def prompt_autocuidado(sintomas: str) -> str:
    """Prompt para protocolo de síntomas leves con orientación domiciliaria"""
    return f"""Eres un médico de atención primaria orientando sobre autocuidado domiciliario.

SÍNTOMAS LEVES REPORTADOS: {sintomas}

INSTRUCCIÓN: Los síntomas son leves y manejables en casa. Da orientación práctica y tranquilizadora.

RESPONDE en este formato:
AUTOCUIDADO: [2-3 medidas concretas que puede hacer en casa]
MEDICACIÓN_SIN_RECETA: [si aplica: medicamento OTC, dosis — si no: "No necesario"]
REPOSO: [recomendación de descanso]
CONSULTA_SI: [síntoma concreto que debería llevarle al médico]"""


def parsear_nivel_urgencia(texto: str) -> str:
    """Extrae el nivel de urgencia del texto de respuesta del triage."""
    texto_upper = texto.upper()
    if "EMERGENCIA" in texto_upper:
        return "EMERGENCIA"
    elif "GRAVE" in texto_upper:
        return "GRAVE"
    elif "MODERADO" in texto_upper:
        return "MODERADO"
    elif "LEVE" in texto_upper:
        return "LEVE"
    return "MODERADO"  # Valor por defecto conservador
