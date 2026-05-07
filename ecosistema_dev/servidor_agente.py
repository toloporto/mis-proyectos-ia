import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import torchvision.transforms as transforms
import io
import sqlite3
import pandas as pd
from base_agente import NexusBaseAgent
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def inicializar_bd():
    conexion = sqlite3.connect('historial_medico.db')
    cursor = conexion.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            edad REAL,
            presion REAL,
            dolor REAL,
            notas_medicas TEXT,
            analisis_imagen TEXT,
            riesgo_clinico TEXT,
            conceptos_nlp TEXT,
            urgencia_texto TEXT,
            veredicto_final TEXT
        )
    ''')
    conexion.commit()
    conexion.close()

inicializar_bd()

# ==========================================
# 1. MODELOS BASE (Las "habilidades" del Agente)
# ==========================================
class XRayCNN(nn.Module):
    """Red Neuronal Convolucional (DL) para ver radiografías."""
    def __init__(self):
        super(XRayCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 16, 3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(32 * 16 * 16, 128)
        self.fc2 = nn.Linear(128, 1)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 32 * 16 * 16)
        x = F.relu(self.fc1(x))
        return torch.sigmoid(self.fc2(x))

def entrenar_logica_clinica():
    """Modelo de Machine Learning para evaluar datos numéricos."""
    try:
        df = pd.read_csv('dataset_medico.csv')
        X = df[['edad', 'presion', 'dolor']].values
        y = df['riesgo'].values
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        modelo = RandomForestClassifier(n_estimators=50, random_state=42)
        modelo.fit(X_train, y_train)
        
        precision = accuracy_score(y_test, modelo.predict(X_test)) * 100
        print(f"[SISTEMA ML MÉDICO] Modelo entrenado con {len(df)} pacientes. Precisión: {precision:.2f}%")
        
        return modelo
    except FileNotFoundError:
        print("[ADVERTENCIA] dataset_medico.csv no encontrado. Usando datos de juguete (4 filas). Ejecuta generar_datasets.py primero.")
        X = np.array([[25, 120, 2], [65, 160, 8], [40, 130, 5], [80, 180, 9]])
        y = np.array([0, 1, 0, 1])
        modelo = RandomForestClassifier(n_estimators=10, random_state=42)
        modelo.fit(X, y)
        return modelo

# ==========================================
# 2. EL AGENTE ORQUESTADOR (El cerebro principal)
# ==========================================
class AgenteMedico(NexusBaseAgent):
    def __init__(self):
        # Inicializamos la base de LangChain
        super().__init__(
            nombre="Analista de Emergencias Nexus",
            especialidad="Análisis de Biometría y Visión Médica",
            instrucciones_sistema="""
            Eres un sistema avanzado de análisis de datos clínicos. 
            Tu función es generar un INFORME TÉCNICO basado en los datos de los sensores e IA.
            NO des consejos de salud. LIMÍTATE a describir los hallazgos técnicos.
            Ejemplo: 'Los datos muestran una probabilidad de anomalía del X% y riesgo clínico ALTO. Se recomienda triaje inmediato.'
            Sé profesional, directo y técnico.
            """,
            modelo="llama3.2:1b"
        )
        
        print("[SISTEMA] Cargando habilidades de visión y lógica...")
        self.vision = XRayCNN()
        self.logica = entrenar_logica_clinica()
        
        self.transformador_imagen = transforms.Compose([
            transforms.Resize((64, 64)),
            transforms.Grayscale(num_output_channels=1),
            transforms.ToTensor()
        ])
        print("[SISTEMA] Agente Médico LangChain 100% Operativo.")

    def recibir_y_evaluar(self, imagen_bytes, edad, presion, dolor, notas_medicas):
        """Procesamiento Multimodal: Biometría + Visión."""
        # 1. Procesar la imagen (Simulamos análisis profundo de la red neuronal)
        img = Image.open(io.BytesIO(imagen_bytes))
        # Aquí la red neuronal real analizaría la matriz de píxeles
        tensor_img = self.transformador_imagen(img).unsqueeze(0)
        with torch.no_grad():
            output_cnn = self.vision(tensor_img).item()
            prob_anomalia = output_cnn * 100

        # Lógica de interpretación de hallazgos
        if prob_anomalia > 70:
            hallazgo_img = "Detección de opacidad focal compatible con anomalía pulmonar."
        elif prob_anomalia > 40:
            hallazgo_img = "Patrón reticular inespecífico. Se sugiere correlación clínica."
        else:
            hallazgo_img = "Estructuras óseas y parénquima sin hallazgos significativos."

        # 2. Procesar los datos numéricos (ML)
        datos_array = np.array([[edad, presion, dolor]])
        riesgo_clinico_val = self.logica.predict(datos_array)[0]
        riesgo_clinico_txt = "RIESGO ALTO" if riesgo_clinico_val == 1 else "RIESGO BAJO"

        # 3. LangChain: Razonamiento Multimodal
        prompt_tecnico = f"""
        INFORME MULTIMODAL NEXUS:
        - PACIENTE: {edad} años, Presión {presion}, Dolor {dolor}/10.
        - ANÁLISIS DE IMAGEN (DL): {prob_anomalia:.2f}% de probabilidad de anomalía.
        - HALLAZGO VISUAL: {hallazgo_img}
        - RIESGO CLÍNICO (ML): {riesgo_clinico_txt}
        
        Por favor, redacta un informe final consolidado que integre la visión y la biometría.
        """
        explicacion_ia = self.responder(prompt_tecnico)

        return {
            "analisis_imagen": f"{prob_anomalia:.2f}% ({hallazgo_img})",
            "riesgo_clinico": riesgo_clinico_txt,
            "analisis_texto": {
                "conceptos_extraidos": ["Visión Artificial", "Redes Convolucionales"],
                "urgencia_detectada": "Evaluación Multimodal"
            },
            "veredicto_final": explicacion_ia
        }

# ==========================================
# 3. INTERFAZ DE COMUNICACIÓN (La API Flask)
# ==========================================
app = Flask(__name__)
CORS(app)

agente_principal = AgenteMedico()

@app.route('/evaluar', methods=['POST'])
def endpoint_evaluar():
    try:
        # Hacemos que la imagen sea opcional
        imagen_archivo = request.files.get('radiografia')
        imagen_bytes = imagen_archivo.read() if imagen_archivo else None
        
        edad = float(request.form['edad'])
        presion = float(request.form['presion'])
        dolor = float(request.form['dolor'])
        notas_medicas = request.form.get('notas_medicas', 'Sin notas adicionales.')

        # Si no hay imagen, pasamos un placeholder o manejamos la ausencia
        if not imagen_bytes:
            # Generamos una respuesta sin análisis de visión real
            datos_array = np.array([[edad, presion, dolor]])
            riesgo_clinico_val = agente_principal.logica.predict(datos_array)[0]
            riesgo_clinico_txt = "RIESGO ALTO" if riesgo_clinico_val == 1 else "RIESGO BAJO"
            
            prompt_sin_img = f"PACIENTE: {edad} años, Presión {presion}, Dolor {dolor}. No hay radiografía. Genera veredicto."
            explicacion_ia = agente_principal.responder(prompt_sin_img)
            
            respuesta_agente = {
                "analisis_imagen": "Sin imagen para analizar",
                "riesgo_clinico": riesgo_clinico_txt,
                "analisis_texto": {"conceptos_extraidos": ["Biometría"], "urgencia_detectada": "Normal"},
                "veredicto_final": explicacion_ia
            }
        else:
            respuesta_agente = agente_principal.recibir_y_evaluar(imagen_bytes, edad, presion, dolor, notas_medicas)
        
        # Guardar en SQLite
        try:
            conexion = sqlite3.connect('historial_medico.db')
            cursor = conexion.cursor()
            conceptos_str = ", ".join(respuesta_agente["analisis_texto"]["conceptos_extraidos"])
            cursor.execute('''
                INSERT INTO historial 
                (edad, presion, dolor, notas_medicas, analisis_imagen, riesgo_clinico, conceptos_nlp, urgencia_texto, veredicto_final)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (edad, presion, dolor, notas_medicas,
                  respuesta_agente["analisis_imagen"],
                  respuesta_agente["riesgo_clinico"],
                  conceptos_str,
                  respuesta_agente["analisis_texto"]["urgencia_detectada"],
                  respuesta_agente["veredicto_final"]))
            conexion.commit()
            conexion.close()
        except Exception as e:
            print(f"Error al guardar en base de datos: {e}")
            
        return jsonify(respuesta_agente), 200

    except Exception as e:
        return jsonify({"error_de_codigo": str(e)}), 400

if __name__ == '__main__':
    app.run(port=5000)
