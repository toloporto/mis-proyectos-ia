from flask import Flask, request, jsonify
from base_agente import NexusBaseAgent

app = Flask(__name__)

class AgenteFarmacia(NexusBaseAgent):
    def recomendar_tratamiento(self, datos_medicos):
        dolor = datos_medicos.get("dolor", 0)
        presion = datos_medicos.get("presion", 120)
        
        recomendaciones = []
        if dolor > 7:
            recomendaciones.append("Analgésicos de alta intensidad (Bajo receta)")
        elif dolor > 3:
            recomendaciones.append("Analgésicos suaves (Paracetamol/Ibuprofeno)")
            
        if presion > 140:
            recomendaciones.append("Hipotensores (Protocolo de hipertensión activo)")
            
        return ", ".join(recomendaciones) if recomendaciones else "Sin medicación inmediata requerida"

# Añadimos los argumentos que faltaban
agente = AgenteFarmacia(
    nombre="Farmacéutico Nexus",
    especialidad="Farmacología y Recomendaciones",
    instrucciones_sistema="Eres un farmacéutico experto. Sugiere tratamientos base basándote en síntomas médicos.",
    modelo="llama3.2:1b"
)

@app.route('/recomendar_farmacia', methods=['POST'])
def recomendar():
    datos = request.json
    receta = agente.recomendar_tratamiento(datos)
    return jsonify({"recomendacion": receta})

if __name__ == '__main__':
    print("[SISTEMA] Agente Farmacéutico Nexus operativo en puerto 5003")
    app.run(port=5003)
