import requests
import io
from PIL import Image

# ==========================================
# 1. CONFIGURACIÓN DEL CLIENTE
# ==========================================
# La ruta absoluta (URL) donde vive nuestro Agente de IA
URL_AGENTE = "http://127.0.0.1:5000/evaluar"

def crear_radiografia_falsa():
    """Crea una imagen negra de 64x64 píxeles en memoria para simular la foto."""
    img = Image.new('L', (64, 64), color=0) # 'L' significa escala de grises
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

# ==========================================
# 2. DATOS DEL PACIENTE (SIMULACIÓN)
# ==========================================
print("--- SISTEMA DEL MÉDICO ---")
print("Recopilando datos del Paciente 001...")

# Simulamos que un médico introduce estos datos
datos_clinicos = {
    "edad": 75,
    "presion": 165,  # Presión alta (riesgo)
    "dolor": 8       # Dolor alto (riesgo)
}

# Simulamos que adjuntamos el archivo de la máquina de Rayos X
archivos = {
    "radiografia": ("xray_paciente001.png", crear_radiografia_falsa(), "image/png")
}

# ==========================================
# 3. ENVÍO DE DATOS Y RESPUESTA
# ==========================================
print(f"Enviando datos al Agente de IA en {URL_AGENTE}...")

try:
    # Hacemos la petición a la API
    respuesta = requests.post(URL_AGENTE, data=datos_clinicos, files=archivos)
    
    # Comprobamos si el Agente respondió correctamente
    if respuesta.status_code == 200:
        veredicto = respuesta.json()
        print("\n=== VEREDICTO DEL AGENTE DE IA ===")
        print(f"🔍 Análisis de Imagen: {veredicto['analisis_imagen']}")
        print(f"📊 Riesgo Clínico:    {veredicto['riesgo_clinico']}")
        print(f"🚨 DECISIÓN FINAL:    {veredicto['veredicto_final']}")
        print("==================================\n")
    else:
        print(f"\n[ERROR] El Agente devolvió un código de error: {respuesta.status_code}")
        print("Detalle:", respuesta.text)

except requests.exceptions.ConnectionError:
    print("\n[ERROR CRÍTICO] No se puede contactar con el Agente de IA.")
    print("Asegúrate de que 'servidor_agente.py' se esté ejecutando en otra terminal.")
