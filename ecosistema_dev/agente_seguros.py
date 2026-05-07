from flask import Flask, request, jsonify
from base_agente import NexusBaseAgent

app = Flask(__name__)

class AgenteSeguros(NexusBaseAgent):
    def evaluar_cobertura(self, datos_medicos):
        riesgo = datos_medicos.get("riesgo_medico", 0)
        
        # Convertimos a string para comparar texto si no es número
        riesgo_str = str(riesgo).upper()
        
        # Nueva lógica que acepta texto y números
        if "ALTO" in riesgo_str or (isinstance(riesgo, (int, float)) and riesgo > 70):
            return "COBERTURA TOTAL (Emergencia crítica bajo póliza Platinum)"
        elif "MEDIO" in riesgo_str or (isinstance(riesgo, (int, float)) and riesgo > 40):
            return "COBERTURA PARCIAL (Requiere aprobación previa)"
        else:
            return "COBERTURA ESTÁNDAR (Consultas preventivas)"

agente = AgenteSeguros(
    nombre="Especialista en Seguros Nexus",
    especialidad="Evaluación de Pólizas Médicas",
    instrucciones_sistema="Evalúa la cobertura basándote en el riesgo médico (numérico o descriptivo).",
    modelo="llama3.2:1b"
)

@app.route('/evaluar_seguro', methods=['POST'])
def evaluar():
    datos = request.json
    cobertura = agente.evaluar_cobertura(datos)
    return jsonify({"cobertura": cobertura})

if __name__ == '__main__':
    app.run(port=5002)
