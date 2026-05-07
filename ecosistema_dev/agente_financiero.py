import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from flask import Flask, request, jsonify
from flask_cors import CORS
from base_agente import NexusBaseAgent

# ==========================================
# 1. MODELOS BASE (Las "habilidades" del Agente Financiero)
# ==========================================
def entrenar_logica_financiera():
    """Modelo de ML para evaluar riesgo crediticio."""
    try:
        df = pd.read_csv('dataset_financiero.csv')
        X = df[['ingresos', 'deuda', 'edad']].values
        y = df['riesgo'].values
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        modelo = RandomForestClassifier(n_estimators=50, random_state=42)
        modelo.fit(X_train, y_train)
        
        precision = accuracy_score(y_test, modelo.predict(X_test)) * 100
        print(f"[SISTEMA ML FINANCIERO] Modelo entrenado con {len(df)} expedientes. Precisión: {precision:.2f}%")
        
        return modelo
    except FileNotFoundError:
        print("[ADVERTENCIA] dataset_financiero.csv no encontrado. Usando datos de juguete (4 filas). Ejecuta generar_datasets.py primero.")
        # Datos: [Ingresos (miles), Deuda (miles), Edad]
        X = np.array([[50, 10, 30], [20, 30, 25], [100, 20, 45], [15, 40, 22]])
        # 0 = Bajo Riesgo (Aprobar), 1 = Alto Riesgo (Rechazar)
        y = np.array([0, 1, 0, 1])
        modelo = RandomForestClassifier(n_estimators=10, random_state=42)
        modelo.fit(X, y)
        return modelo

# ==========================================
# 2. EL AGENTE ORQUESTADOR FINANCIERO
# ==========================================
class AgenteFinanciero(NexusBaseAgent):
    def __init__(self):
        # Inicializamos LangChain
        super().__init__(
            nombre="Auditor de Riesgos Nexus",
            especialidad="Análisis de Solvencia y Scoring Bancario",
            instrucciones_sistema="""
            Eres un auditor de riesgos financieros. 
            Tu labor es emitir un DICTAMEN DE SOLVENCIA basado en los datos del cliente.
            Analiza los ingresos, deudas y el riesgo calculado por el modelo de ML.
            Sé formal, utiliza términos bancarios y concluye si el perfil es APTO o NO APTO.
            """,
            modelo="llama3.2:1b"
        )
        print("[SISTEMA] Cargando lógica financiera...")
        self.logica = entrenar_logica_financiera()
        print("[SISTEMA] Agente Financiero LangChain 100% Operativo.")

    def evaluar_credito(self, ingresos, deuda, edad, notas_financieras):
        """Función principal para tomar decisión de crédito con LangChain."""
        # 1. ML
        datos_array = np.array([[ingresos, deuda, edad]])
        riesgo_ml_val = self.logica.predict(datos_array)[0]
        riesgo_ml_txt = "Alto" if riesgo_ml_val == 1 else "Bajo"

        # 2. LangChain Razonamiento
        prompt_financiero = f"""
        SOLICITANTE: Edad {edad}, Ingresos {ingresos}k, Deuda {deuda}k.
        RESULTADOS TÉCNICOS:
        - Riesgo Predictivo (ML): {riesgo_ml_txt}
        - Historial reportado: {notas_financieras}
        
        Por favor, genera un informe de aprobación o rechazo.
        """
        explicacion_ia = self.responder(prompt_financiero)

        return {
            "riesgo_tabular": riesgo_ml_txt,
            "analisis_texto": {
                "conceptos_extraidos": ["Finanzas via LLM"],
                "alerta_texto": "Evaluado por LangChain"
            },
            "veredicto_final": explicacion_ia
        }

# ==========================================
# 3. INTERFAZ DE COMUNICACIÓN (La API Flask)
# ==========================================
app = Flask(__name__)
CORS(app)

agente_financiero = AgenteFinanciero()

@app.route('/evaluar_credito', methods=['POST'])
def endpoint_evaluar():
    try:
        ingresos = float(request.form['ingresos'])
        deuda = float(request.form['deuda'])
        edad = float(request.form['edad'])
        notas_financieras = request.form.get('notas_financieras', 'Sin notas.')

        respuesta = agente_financiero.evaluar_credito(ingresos, deuda, edad, notas_financieras)
        
        return jsonify(respuesta), 200

    except Exception as e:
        return jsonify({"error_de_codigo": str(e)}), 400

if __name__ == '__main__':
    # El agente financiero corre en el puerto 5001
    app.run(port=5001)
