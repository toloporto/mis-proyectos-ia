# src/tools/validador_sintomas.py - Versión mejorada
import re

def validar_sintomas(texto: str) -> dict:
    """Versión mejorada que detecta más síntomas y variaciones"""
    texto = texto.lower()
    
    # Diccionario de síntomas con sinónimos y variaciones
    sintomas_dict = {
        # Dolor y molestias
        "dolor": ["dolor", "duele", "dolores", "doloroso", "dolencia"],
        "cabeza": ["cabeza", "cefalea", "migraña", "dolor de cabeza"],
        "pecho": ["pecho", "torácico", "pecho", "opresión pecho"],
        
        # Problemas respiratorios
        "dificultad_respirar": ["respirar", "respiración", "falta de aire", "ahogo", "disnea", "resuello"],
        "tos": ["tos", "toser", "tos seca", "tos con flema"],
        
        # Síntomas generales
        "fiebre": ["fiebre", "temperatura", "calentura", "febrícula"],
        "fatiga": ["fatiga", "cansancio", "agotamiento", "debilidad", "falta energía"],
        "nausea": ["nausea", "náusea", "mareo", "vertigo", "vomitar", "vómito"],
        
        # Síntomas cardiovasculares
        "presion": ["presión", "hipertensión", "tensión alta", "presión alta"],
        "palpitaciones": ["palpitaciones", "corazón acelerado", "taquicardia", "arritmia"],
        
        # Síntomas neurológicos
        "mareo": ["mareo", "vértigo", "aturdimiento", "inestabilidad"],
    }
    
    sintomas_encontrados = []
    
    # Buscar cada síntoma y sus sinónimos
    for sintoma_principal, variaciones in sintomas_dict.items():
        for variacion in variaciones:
            if variacion in texto:
                # Limpiar el nombre del síntoma para mostrarlo bonito
                nombre_mostrar = sintoma_principal.replace("_", " ")
                if nombre_mostrar not in sintomas_encontrados:
                    sintomas_encontrados.append(nombre_mostrar)
                break  # Una vez encontrado, pasar al siguiente síntoma
    
    # Si no se encontró nada, buscar palabras sueltas comunes
    if not sintomas_encontrados:
        palabras_comunes = ["dolor", "mal", "molestia", "enfermo", "síntoma"]
        for palabra in palabras_comunes:
            if palabra in texto:
                sintomas_encontrados.append(f"síntoma leve: {palabra}")
    
    return {
        "sintomas_encontrados": sintomas_encontrados,
        "cantidad": len(sintomas_encontrados),
        "texto_original": texto,
        "detalles": {
            "tiene_dolor": "dolor" in texto,
            "tiene_fiebre": "fiebre" in texto,
            "tiene_dificultad_respiratoria": any(r in texto for r in ["respirar", "falta de aire", "ahogo"])
        }
    }

def calcular_urgencia(sintomas: list) -> str:
    """Versión mejorada que calcula urgencia de forma más precisa"""
    sintomas_str = " ".join(sintomas).lower()
    
    # Nivel ROJO - EMERGENCIA (vida en peligro)
    criterios_rojo = [
        "dificultad respirar" in sintomas_str,
        "respirar" in sintomas_str,
        "falta de aire" in sintomas_str,
        "dolor pecho" in sintomas_str,
        "presion" in sintomas_str,
        "palpitaciones" in sintomas_str,
        "desmayo" in sintomas_str,
    ]
    
    # Nivel AMARILLO - URGENTE (requiere atención pronto)
    criterios_amarillo = [
        "fiebre" in sintomas_str and "cabeza" in sintomas_str,
        "vomitar" in sintomas_str,
        "mareo" in sintomas_str and "nausea" in sintomas_str,
        len(sintomas) >= 3,
        "dolor" in sintomas_str and len(sintomas) >= 2,
    ]
    
    if any(criterios_rojo):
        return "🔴 ROJO - EMERGENCIA: Requiere atención médica INMEDIATA"
    elif any(criterios_amarillo):
        return "🟡 AMARILLO - URGENTE: Atender en menos de 30 minutos"
    elif len(sintomas) >= 2:
        return "🟢 VERDE - PRIORIDAD: Programar cita en las próximas 24 horas"
    elif len(sintomas) == 1:
        return "🔵 AZUL - LEVE: Seguimiento normal en consulta externa"
    else:
        return "⚪ BLANCO - INFORMATIVO: Consulta administrativa o sin síntomas claros"

# Añade esta función al final del archivo validador_sintomas.py si no existe

def obtener_recomendacion(sintomas: list, urgencia: str) -> str:
    """Recomendación basada en síntomas y nivel de urgencia"""
    if "ROJO" in urgencia:
        return "🚨 LLAME AL 911 o ACUDA A EMERGENCIAS INMEDIATAMENTE"
    elif "AMARILLO" in urgencia:
        return "📞 Contacte a su médico de cabecera o acuda a urgencias en las próximas horas"
    elif "VERDE" in urgencia:
        return "📅 Solicite una cita médica prioritaria para hoy o mañana"
    elif "AZUL" in urgencia:
        return "💊 Consulte con farmacia o agende consulta general en los próximos días"
    else:
        return "ℹ️ Si los síntomas persisten, consulte con un profesional de salud"