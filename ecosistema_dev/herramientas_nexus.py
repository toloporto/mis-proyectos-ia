from langchain.tools import tool
import numpy as np
import torch
from PIL import Image
import io
import pandas as pd

# Nota: Importamos las funciones de entrenamiento y las clases de los agentes originales
# Para este paso, asumimos que los modelos ya están cargados en memoria.

@tool
def herramienta_analisis_clinico(edad: int, presion: int, dolor: int) -> str:
    """Analiza los signos vitales del paciente usando un modelo de Machine Learning (Random Forest)."""
    # En un entorno real, cargaríamos el modelo guardado. Aquí simulamos la lógica:
    riesgo = 1 if (presion > 150 or dolor > 7) else 0
    return "ALTO RIESGO" if riesgo == 1 else "RIESGO BAJO"

@tool
def herramienta_analisis_financiero(ingresos: int, deuda: int, edad: int) -> str:
    """Evalúa el riesgo crediticio basándose en ingresos, deuda y edad."""
    riesgo = 1 if (deuda > ingresos * 0.4) else 0
    return "PERFIL NO APTO (Riesgo de impago)" if riesgo == 1 else "PERFIL APTO"

@tool
def herramienta_vision_xray(imagen_path: str) -> str:
    """Analiza una radiografía para detectar anomalías mediante una red neuronal (CNN)."""
    # Simulación de la respuesta de la CNN que ya tienes en servidor_agente.py
    import random
    prob = random.uniform(0, 100)
    return f"Probabilidad de anomalía detectada: {prob:.2f}%"

print("[SISTEMA] Herramientas Nexus (Tools) registradas correctamente.")
