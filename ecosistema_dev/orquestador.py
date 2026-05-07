from flask import Flask, request, jsonify
from flask_cors import CORS
from grafo_nexus import app_nexus
from langchain_core.messages import HumanMessage, AIMessage
import sqlite3

app = Flask(__name__)
CORS(app)

@app.route('/sesiones', methods=['GET'])
def listar_sesiones():
    try:
        conn = sqlite3.connect('nexus_memory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT thread_id FROM checkpoints')
        sesiones = [fila[0] for fila in cursor.fetchall()]
        conn.close()
        return jsonify({"sesiones": sesiones})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/cargar_sesion/<thread_id>', methods=['GET'])
def cargar_sesion(thread_id):
    try:
        config = {"configurable": {"thread_id": thread_id}}
        estado = app_nexus.get_state(config)
        
        if not estado.values:
            return jsonify({"error": "Sesión no encontrada"}), 404
            
        mensajes = []
        for msg in estado.values.get("messages", []):
            role = "user" if isinstance(msg, HumanMessage) else "nexus"
            mensajes.append({"role": role, "content": msg.content})
            
        return jsonify({
            "mensajes": mensajes,
            "resultados_tecnicos": estado.values.get("resultados_tecnicos", {}),
            "datos_extraidos": estado.values.get("datos_extraidos", {})
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/orquestar', methods=['POST'])
def orquestar():
    datos = request.json
    texto_usuario = datos.get("mensaje", "")
    thread_id = datos.get("session_id", "sesion_usuario_provisional")
    
    if not texto_usuario:
        return jsonify({"error": "No se proporcionó un mensaje."}), 400
        
    print(f"[NEXUS] Ejecutando Grafo con memoria (ID: {thread_id}) para: '{texto_usuario}'")
    config = {"configurable": {"thread_id": thread_id}}
    
    inputs = {
        "messages": [HumanMessage(content=texto_usuario)],
        "mensaje_usuario": texto_usuario
    }
    
    final_state = app_nexus.invoke(inputs, config=config)
    agente_destino = final_state["agente_actual"]
    
    respuesta = {
        "agente": agente_destino.capitalize(),
        "descripcion": final_state.get("decision_final", ""),
        "datos_extraidos": final_state.get("datos_extraidos", {}),
        "resultados_tecnicos": final_state.get("resultados_tecnicos", {}),
        "formulario_requerido": "ninguno"
    }
    
    if agente_destino == "medico":
        respuesta.update({"url_destino": "http://127.0.0.1:5000/evaluar", "formulario_requerido": "form_medico"})
    elif agente_destino == "financiero":
        respuesta.update({"url_destino": "http://127.0.0.1:5001/evaluar_credito", "formulario_requerido": "form_financiero"})
    
    return jsonify(respuesta), 200

if __name__ == '__main__':
    print("[NEXUS] Orquestador v5.0 (Historial) operativo en puerto 8000")
    app.run(port=8000)
