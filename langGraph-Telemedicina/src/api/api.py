# src/api/api.py
# API REST PARA EL SISTEMA MULTIAGENTE - VERSIÓN OPTIMIZADA

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import sys
import os
import time
import asyncio
import requests
from contextlib import asynccontextmanager

# Añadir rutas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.database import db

# ============================================
# CONFIGURACIÓN
# ============================================

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "phi3:latest"
TIMEOUT = 30
MAX_TOKENS = 80

# Modelo para OpenAI (alternativo, si se quiere usar)
OPENAI_MODEL = None

# ============================================
# CICLO DE VIDA DE LA APLICACIÓN
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja el inicio y cierre de la aplicación"""
    print("\n" + "="*50)
    print("🚀 INICIANDO API DEL SISTEMA MULTIAGENTE")
    print("="*50)
    print(f"\n📦 Modelo: {MODELO}")
    print(f"⏱️  Timeout: {TIMEOUT}s")
    print(f"💾 Base de datos: SQLite")
    print("\n📌 Endpoints disponibles:")
    print("   • http://localhost:8000/ - API info")
    print("   • http://localhost:8000/web - Interfaz web")
    print("   • http://localhost:8000/docs - Documentación Swagger")
    print("\n🔧 Presiona Ctrl+C para detener")
    print("="*50 + "\n")
    
    yield
    
    print("\n🛑 Cerrando API...")
    db.close()
    print("✅ API cerrada correctamente")

# Crear aplicación con lifespan
app = FastAPI(
    title="Sistema Multiagente Médico API", 
    description="API para consultas médicas con IA multiagente (Triage → Diagnóstico → Tratamiento)",
    version="2.1",
    lifespan=lifespan
)

# CORS para permitir conexiones desde web/app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# MODELOS DE DATOS
# ============================================

class ConsultaRequest(BaseModel):
    sintomas: str
    nombre_paciente: Optional[str] = None
    edad: Optional[int] = 0

class ConsultaResponse(BaseModel):
    id: int
    sintomas: str
    triage: str
    diagnostico: str
    tratamiento: str
    nivel_urgencia: str
    tiempo_procesamiento: float
    timestamp: str

class StatsResponse(BaseModel):
    total_consultas: int
    total_pacientes: int
    tiempo_promedio: float
    distribucion_urgencias: Dict[str, int]

# ============================================
# FUNCIONES DEL SISTEMA MULTIAGENTE
# ============================================

def consultar_ollama(prompt: str, temperatura: float = 0.2) -> tuple:
    """
    Consulta Ollama con manejo de errores mejorado.
    Retorna (respuesta, tiempo_ejecucion)
    """
    inicio = time.time()
    
    try:
        respuesta = requests.post(
            OLLAMA_URL,
            json={
                "model": MODELO,
                "prompt": prompt,
                "stream": False,
                "temperature": temperatura,
                "max_tokens": MAX_TOKENS,
                "num_predict": MAX_TOKENS - 20
            },
            timeout=TIMEOUT
        )
        tiempo = time.time() - inicio
        
        if respuesta.status_code == 200:
            resultado = respuesta.json()["response"].strip()
            # Limpiar respuestas con código
            if any(x in resultado for x in ["import", "def ", "```", "class ", "hashlib"]):
                return "Consulta médica recomendada", tiempo
            # Limitar longitud
            if len(resultado) > 150:
                resultado = resultado[:147] + "..."
            return resultado if resultado else "Evaluación médica", tiempo
        return f"Error: {respuesta.status_code}", tiempo
        
    except requests.exceptions.Timeout:
        tiempo = time.time() - inicio
        return "Consulta médica - El sistema está procesando", tiempo
    except requests.exceptions.ConnectionError:
        return "Error: Ollama no está corriendo", 0
    except Exception as e:
        return f"Error: {str(e)[:50]}", 0

def extraer_nivel_urgencia(texto: str) -> str:
    """Extrae el nivel de urgencia de la respuesta del triage"""
    texto_mayus = texto.upper()
    if "EMERGENCIA" in texto_mayus:
        return "EMERGENCIA"
    elif "GRAVE" in texto_mayus:
        return "GRAVE"
    elif "MODERADO" in texto_mayus:
        return "MODERADO"
    elif "LEVE" in texto_mayus:
        return "LEVE"
    return "NO_CLASIFICADO"

async def ejecutar_multiagente(sintomas: str) -> Dict[str, Any]:
    """
    Ejecuta el sistema multiagente con 3 agentes:
    1. Triage - Clasifica urgencia
    2. Diagnóstico - Identifica condición
    3. Tratamiento - Recomienda acciones
    """
    
    # AGENTE 1: TRIAGE
    print("   🟡 Agente Triage: Clasificando urgencia...")
    triage_prompt = f"Síntomas: {sintomas}\nNivel de urgencia (LEVE/MODERADO/GRAVE/EMERGENCIA):"
    triage_respuesta, triage_tiempo = consultar_ollama(triage_prompt, 0.1)
    nivel_urgencia = extraer_nivel_urgencia(triage_respuesta)
    
    # AGENTE 2: DIAGNÓSTICO
    print("   🔵 Agente Diagnóstico: Analizando condición...")
    diagnostico_prompt = f"Síntomas: {sintomas}\nPosible diagnóstico en 1 frase:"
    diagnostico_respuesta, diagnostico_tiempo = consultar_ollama(diagnostico_prompt, 0.2)
    
    # AGENTE 3: TRATAMIENTO
    print("   🟢 Agente Tratamiento: Generando recomendación...")
    tratamiento_prompt = f"Para síntomas: {sintomas}\nRecomendación médica en 1 frase:"
    tratamiento_respuesta, tratamiento_tiempo = consultar_ollama(tratamiento_prompt, 0.25)
    
    return {
        "triage": triage_respuesta,
        "diagnostico": diagnostico_respuesta,
        "tratamiento": tratamiento_respuesta,
        "nivel_urgencia": nivel_urgencia,
        "tiempos": {
            "triage": round(triage_tiempo, 1),
            "diagnostico": round(diagnostico_tiempo, 1),
            "tratamiento": round(tratamiento_tiempo, 1)
        }
    }

# ============================================
# ENDPOINTS DE LA API
# ============================================

@app.get("/")
async def root():
    return {
        "api": "Sistema Multiagente Médico",
        "version": "2.1",
        "modelo": MODELO,
        "agentes": ["Triage", "Diagnóstico", "Tratamiento"],
        "endpoints": {
            "/consultar": "POST - Realizar consulta médica",
            "/estadisticas": "GET - Obtener estadísticas",
            "/consultas": "GET - Listar consultas",
            "/pacientes": "GET - Listar pacientes",
            "/web": "GET - Interfaz web",
            "/docs": "GET - Documentación Swagger"
        }
    }

@app.get("/health")
async def health_check():
    """Verifica el estado del sistema"""
    # Verificar Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        ollama_status = response.status_code == 200
    except:
        ollama_status = False
    
    return {
        "status": "healthy" if ollama_status else "degraded",
        "ollama": "connected" if ollama_status else "disconnected",
        "modelo": MODELO,
        "database": "connected"
    }

@app.post("/consultar", response_model=ConsultaResponse)
async def consultar(request: ConsultaRequest, background_tasks: BackgroundTasks):
    """
    Realiza una consulta médica usando el sistema multiagente
    
    - **sintomas**: Descripción de los síntomas del paciente
    - **nombre_paciente**: Nombre del paciente (opcional)
    - **edad**: Edad del paciente (opcional)
    """
    if not request.sintomas or len(request.sintomas.strip()) < 5:
        raise HTTPException(status_code=400, detail="Describe tus síntomas con más detalle (mínimo 5 caracteres)")
    
    inicio_total = time.time()
    
    try:
        # Crear paciente
        paciente_id = db.crear_paciente(request.nombre_paciente, request.edad)
        
        # Ejecutar multiagente
        resultados = await ejecutar_multiagente(request.sintomas)
        tiempo_total = time.time() - inicio_total
        
        # Añadir tiempo total a resultados
        resultados['tiempos']['total'] = round(tiempo_total, 1)
        
        # Guardar en BD
        consulta_id = db.guardar_consulta({
            'paciente_id': paciente_id,
            'sintomas': request.sintomas,
            'triage': resultados['triage'],
            'diagnostico': resultados['diagnostico'],
            'tratamiento': resultados['tratamiento'],
            'nivel_urgencia': resultados['nivel_urgencia'],
            'tiempo_procesamiento': tiempo_total,
            'modelo_ia': MODELO
        })
        
        return ConsultaResponse(
            id=consulta_id,
            sintomas=request.sintomas,
            triage=resultados['triage'],
            diagnostico=resultados['diagnostico'],
            tratamiento=resultados['tratamiento'],
            nivel_urgencia=resultados['nivel_urgencia'],
            tiempo_procesamiento=tiempo_total,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la consulta: {str(e)}")

@app.get("/estadisticas", response_model=StatsResponse)
async def get_estadisticas():
    """Obtiene estadísticas del sistema desde la base de datos"""
    stats = db.obtener_estadisticas()
    
    return StatsResponse(
        total_consultas=stats.get('total_consultas', 0),
        total_pacientes=stats.get('total_pacientes', 0),
        tiempo_promedio=round(stats.get('tiempo_promedio', 0), 1),
        distribucion_urgencias={}
    )

@app.get("/consultas")
async def listar_consultas(limite: int = 10, offset: int = 0):
    """
    Lista las últimas consultas
    
    - **limite**: Número de consultas a mostrar (máx 50)
    - **offset**: Desplazamiento para paginación
    """
    limite = min(limite, 50)  # Máximo 50 consultas
    consultas = db.obtener_consultas(limite)
    return {
        "consultas": consultas, 
        "total": len(consultas),
        "limite": limite,
        "offset": offset
    }

@app.get("/pacientes")
async def listar_pacientes(limite: int = 20):
    """Lista los pacientes registrados"""
    cursor = db.conn.execute(
        "SELECT id, nombre, edad, created_at FROM pacientes ORDER BY created_at DESC LIMIT ?",
        (limite,)
    )
    pacientes = [dict(row) for row in cursor.fetchall()]
    return {"pacientes": pacientes, "total": len(pacientes)}

@app.get("/consultas/paciente/{paciente_id}")
async def consultas_por_paciente(paciente_id: int):
    """Obtiene todas las consultas de un paciente específico"""
    cursor = db.conn.execute(
        "SELECT * FROM consultas WHERE paciente_id = ? ORDER BY created_at DESC",
        (paciente_id,)
    )
    consultas = [dict(row) for row in cursor.fetchall()]
    
    # Obtener información del paciente
    cursor = db.conn.execute(
        "SELECT nombre, edad FROM pacientes WHERE id = ?",
        (paciente_id,)
    )
    paciente = cursor.fetchone()
    
    return {
        "paciente_id": paciente_id, 
        "paciente_nombre": paciente['nombre'] if paciente else None,
        "consultas": consultas,
        "total_consultas": len(consultas)
    }

@app.delete("/consultas/{consulta_id}")
async def eliminar_consulta(consulta_id: int):
    """Elimina una consulta específica (solo para administración)"""
    cursor = db.conn.execute(
        "DELETE FROM consultas WHERE id = ?",
        (consulta_id,)
    )
    db.conn.commit()
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")
    
    return {"message": f"Consulta {consulta_id} eliminada", "success": True}

# ============================================
# INTERFAZ WEB MEJORADA
# ============================================

HTML_WEB = """
<!DOCTYPE html>
<html>
<head>
    <title>Sistema Multiagente Médico</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 700px; margin: auto; background: white; padding: 30px; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
        h1 { color: #2c3e50; margin-top: 0; display: flex; align-items: center; gap: 10px; }
        h1:before { content: "🏥"; font-size: 2em; }
        .badge { display: inline-block; background: #e9ecef; padding: 5px 10px; border-radius: 20px; font-size: 12px; margin: 0 5px; }
        textarea { width: 100%; height: 120px; margin: 15px 0; padding: 12px; border: 2px solid #ddd; border-radius: 10px; font-family: monospace; font-size: 14px; resize: vertical; transition: border-color 0.3s; }
        textarea:focus { outline: none; border-color: #667eea; }
        input { width: calc(50% - 6px); padding: 10px; margin: 5px 3px; border: 2px solid #ddd; border-radius: 8px; transition: border-color 0.3s; }
        input:focus { outline: none; border-color: #667eea; }
        button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 14px 28px; border: none; border-radius: 10px; cursor: pointer; font-size: 16px; font-weight: bold; width: 100%; margin: 15px 0; transition: transform 0.2s, box-shadow 0.2s; }
        button:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(0,0,0,0.2); }
        button:active { transform: translateY(0); }
        .loading { text-align: center; padding: 30px; background: #f8f9fa; border-radius: 10px; display: none; margin: 20px 0; }
        .spinner { width: 40px; height: 40px; border: 4px solid #ddd; border-top-color: #667eea; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 15px; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .resultado { margin-top: 25px; padding: 20px; background: #f8f9fa; border-radius: 15px; display: none; animation: fadeIn 0.5s; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .triage { background: #fee; border-left: 4px solid #dc3545; padding: 12px; margin: 10px 0; border-radius: 8px; }
        .diagnostico { background: #efe; border-left: 4px solid #28a745; padding: 12px; margin: 10px 0; border-radius: 8px; }
        .tratamiento { background: #eef; border-left: 4px solid #17a2b8; padding: 12px; margin: 10px 0; border-radius: 8px; }
        .tiempo { color: #6c757d; text-align: center; margin-top: 15px; font-size: 14px; }
        .error { background: #f8d7da; color: #721c24; padding: 12px; border-radius: 8px; margin: 10px 0; display: none; }
        .info-agentes { display: flex; justify-content: space-around; margin: 20px 0; flex-wrap: wrap; gap: 10px; }
        .agente-card { background: #f0f0f0; padding: 10px 15px; border-radius: 10px; text-align: center; flex: 1; min-width: 80px; }
        .agente-icon { font-size: 24px; }
        .agente-nombre { font-size: 12px; color: #666; margin-top: 5px; }
        hr { margin: 20px 0; border: none; border-top: 1px solid #eee; }
        @media (max-width: 600px) { .container { padding: 20px; } input { width: 100%; margin: 5px 0; } }
    </style>
</head>
<body>
    <div class="container">
        <h1>Sistema Multiagente Médico</h1>
        <p>🤖 <strong>3 agentes IA</strong> trabajan en cadena: <strong>TRIAGE → DIAGNÓSTICO → TRATAMIENTO</strong></p>
        
        <div class="info-agentes">
            <div class="agente-card"><div class="agente-icon">🟡</div><div class="agente-nombre">TRIAGE</div></div>
            <div class="agente-card"><div class="agente-icon">🔵</div><div class="agente-nombre">DIAGNÓSTICO</div></div>
            <div class="agente-card"><div class="agente-icon">🟢</div><div class="agente-nombre">TRATAMIENTO</div></div>
        </div>
        
        <textarea id="sintomas" placeholder="Describe tus síntomas detalladamente&#10;Ej: Tengo dolor de cabeza, mareos y náuseas desde hace 2 días"></textarea>
        <div style="display: flex; gap: 6px;">
            <input type="text" id="nombre" placeholder="Tu nombre (opcional)">
            <input type="number" id="edad" placeholder="Edad (opcional)">
        </div>
        
        <button onclick="consultar()">🔍 Realizar Consulta Médica</button>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <div>⏳ Procesando con 3 agentes IA...</div>
            <div style="font-size: 12px; margin-top: 10px;">Triage → Diagnóstico → Tratamiento</div>
        </div>
        
        <div class="error" id="error"></div>
        
        <div class="resultado" id="resultado">
            <h3 style="margin-top: 0;">📊 Resultados del Sistema Multiagente</h3>
            <div class="triage" id="triage"></div>
            <div class="diagnostico" id="diagnostico"></div>
            <div class="tratamiento" id="tratamiento"></div>
            <div class="tiempo" id="tiempo"></div>
        </div>
        
        <hr>
        <div style="font-size: 12px; color: #999; text-align: center;">
            ⚡ Modelo: phi3 | 🧠 3 agentes IA | 💾 Consultas guardadas
        </div>
    </div>
    
    <script>
        async function consultar() {
            const sintomas = document.getElementById('sintomas').value.trim();
            if (!sintomas) {
                mostrarError('Por favor describe tus síntomas');
                return;
            }
            
            if (sintomas.length < 5) {
                mostrarError('Por favor describe tus síntomas con más detalle');
                return;
            }
            
            ocultarError();
            document.getElementById('loading').style.display = 'block';
            document.getElementById('resultado').style.display = 'none';
            
            try {
                const startTime = Date.now();
                const response = await fetch('/consultar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        sintomas: sintomas,
                        nombre_paciente: document.getElementById('nombre').value.trim() || null,
                        edad: parseInt(document.getElementById('edad').value) || 0
                    })
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Error en la consulta');
                }
                
                const data = await response.json();
                const endTime = Date.now();
                const tiempo = ((endTime - startTime) / 1000).toFixed(1);
                
                document.getElementById('triage').innerHTML = '🔴 <strong>TRIAGE:</strong><br>' + (data.triage || 'No disponible');
                document.getElementById('diagnostico').innerHTML = '🩺 <strong>DIAGNÓSTICO:</strong><br>' + (data.diagnostico || 'No disponible');
                document.getElementById('tratamiento').innerHTML = '💊 <strong>TRATAMIENTO:</strong><br>' + (data.tratamiento || 'No disponible');
                document.getElementById('tiempo').innerHTML = '⏱️ Tiempo total: ' + tiempo + ' segundos<br>🏥 Nivel de urgencia: ' + (data.nivel_urgencia || 'No clasificado');
                
                document.getElementById('resultado').style.display = 'block';
            } catch (error) {
                mostrarError('Error: ' + error.message);
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
        
        function mostrarError(mensaje) {
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = mensaje;
            errorDiv.style.display = 'block';
            setTimeout(() => { errorDiv.style.display = 'none'; }, 5000);
        }
        
        function ocultarError() {
            document.getElementById('error').style.display = 'none';
        }
        
        // Permitir Enter en el textarea
        document.getElementById('sintomas').addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                consultar();
            }
        });
    </script>
</body>
</html>
"""

@app.get("/web", response_class=HTMLResponse)
async def interfaz_web():
    """Interfaz web mejorada para probar la API"""
    return HTMLResponse(content=HTML_WEB)

# ============================================
# PUNTO DE ENTRADA
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )