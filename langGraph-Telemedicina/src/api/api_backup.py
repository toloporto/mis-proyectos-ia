# src/api/api.py
# API REST PARA EL SISTEMA MULTIAGENTE - VERSIÓN PROFESIONAL CON CACHÉ Y RATE LIMITING

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
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

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import db
from cache.cache_manager import cache_manager
from utils.logger import get_logger
from config.settings import settings
from middleware.rate_limit import RateLimitMiddleware

# ============================================
# CONFIGURACIÓN
# ============================================

OLLAMA_URL = settings.OLLAMA_URL
MODELO = settings.DEFAULT_MODEL
TIMEOUT = settings.MODEL_TIMEOUT
MAX_TOKENS = settings.MAX_TOKENS

# Logger
logger = get_logger("api")

# ============================================
# CICLO DE VIDA DE LA APLICACIÓN
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja el inicio y cierre de la aplicación"""
    logger.info("="*50)
    logger.info("🚀 INICIANDO API DEL SISTEMA MULTIAGENTE")
    logger.info("="*50)
    logger.info(f"📦 Modelo: {MODELO}")
    logger.info(f"⏱️  Timeout: {TIMEOUT}s")
    logger.info(f"💾 Base de datos: SQLite")
    logger.info(f"⚡ Caché: {cache_manager.get_stats()['type']}")
    logger.info("")
    logger.info("📌 Endpoints disponibles:")
    logger.info("   • http://localhost:8000/ - API info")
    logger.info("   • http://localhost:8000/web - Interfaz web")
    logger.info("   • http://localhost:8000/docs - Documentación Swagger")
    logger.info("   • http://localhost:8000/health - Health check")
    logger.info("")
    logger.info("🔧 Presiona Ctrl+C para detener")
    logger.info("="*50)
    
    yield
    
    logger.info("🛑 Cerrando API...")
    db.close()
    logger.info("✅ API cerrada correctamente")

# Crear aplicación con lifespan
app = FastAPI(
    title=settings.API_TITLE,
    description="API profesional para consultas médicas con IA multiagente (Triage → Diagnóstico → Tratamiento)",
    version=settings.API_VERSION,
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

# Añadir middleware de rate limiting
app.add_middleware(RateLimitMiddleware)

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
    from_cache: bool = False
    timestamp: str

class StatsResponse(BaseModel):
    total_consultas: int
    total_pacientes: int
    tiempo_promedio: float
    distribucion_urgencias: Dict[str, int]

class HealthResponse(BaseModel):
    status: str
    ollama: str
    modelo: str
    database: str
    cache: str
    timestamp: str

# ============================================
# FUNCIONES DEL SISTEMA MULTIAGENTE
# ============================================

def consultar_ollama(prompt: str, temperatura: float = 0.2, agente: str = "") -> tuple:
    """Consulta Ollama con manejo de errores mejorado"""
    inicio = time.time()
    
    try:
        logger.debug(f"Consultando agente {agente}...")
        
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
                resultado = "Consulta médica recomendada"
            # Limitar longitud
            if len(resultado) > 200:
                resultado = resultado[:197] + "..."
            logger.info(f"Agente {agente} respondió en {tiempo:.1f}s")
            return resultado, tiempo
        return f"Error: {respuesta.status_code}", tiempo
        
    except requests.exceptions.Timeout:
        logger.warning(f"Timeout en agente {agente} después de {TIMEOUT}s")
        return "Consulta médica - El sistema está procesando", TIMEOUT
    except requests.exceptions.ConnectionError:
        logger.error("Error de conexión con Ollama")
        return "Error: Ollama no está corriendo", 0
    except Exception as e:
        logger.error(f"Error en agente {agente}: {e}")
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

async def ejecutar_multiagente(sintomas: str, uso_caché: bool = True) -> Dict[str, Any]:
    """
    Ejecuta el sistema multiagente con 3 agentes:
    1. Triage - Clasifica urgencia
    2. Diagnóstico - Identifica condición
    3. Tratamiento - Recomienda acciones
    """
    
    # Verificar caché primero
    if uso_caché:
        cached_result = await cache_manager.get_consulta(sintomas)
        if cached_result:
            logger.info(f"✅ Respuesta desde caché para: {sintomas[:50]}...")
            return cached_result
    
    logger.info(f"🔄 Ejecutando agentes para: {sintomas[:50]}...")
    
    # AGENTE 1: TRIAGE
    logger.debug("   🟡 Agente Triage: Clasificando urgencia...")
    triage_prompt = f"Síntomas: {sintomas}\nNivel de urgencia (LEVE/MODERADO/GRAVE/EMERGENCIA):"
    triage_respuesta, triage_tiempo = consultar_ollama(triage_prompt, 0.1, "triage")
    nivel_urgencia = extraer_nivel_urgencia(triage_respuesta)
    
    # AGENTE 2: DIAGNÓSTICO
    logger.debug("   🔵 Agente Diagnóstico: Analizando condición...")
    diagnostico_prompt = f"Síntomas: {sintomas}\nPosible diagnóstico en 1 frase:"
    diagnostico_respuesta, diagnostico_tiempo = consultar_ollama(diagnostico_prompt, 0.2, "diagnostico")
    
    # AGENTE 3: TRATAMIENTO
    logger.debug("   🟢 Agente Tratamiento: Generando recomendación...")
    tratamiento_prompt = f"Para síntomas: {sintomas}\nRecomendación médica en 1 frase:"
    tratamiento_respuesta, tratamiento_tiempo = consultar_ollama(tratamiento_prompt, 0.25, "tratamiento")
    
    resultado = {
        "triage": triage_respuesta,
        "diagnostico": diagnostico_respuesta,
        "tratamiento": tratamiento_respuesta,
        "nivel_urgencia": nivel_urgencia,
        "tiempos": {
            "triage": round(triage_tiempo, 1),
            "diagnostico": round(diagnostico_tiempo, 1),
            "tratamiento": round(tratamiento_tiempo, 1),
            "total": round(triage_tiempo + diagnostico_tiempo + tratamiento_tiempo, 1)
        }
    }
    
    # Guardar en caché
    if uso_caché:
        await cache_manager.set_consulta(sintomas, 0, resultado)
        logger.info(f"💾 Resultado guardado en caché")
    
    return resultado

# ============================================
# ENDPOINTS DE LA API
# ============================================

@app.get("/")
async def root():
    """Información de la API"""
    return {
        "api": "Sistema Multiagente Médico",
        "version": settings.API_VERSION,
        "modelo": MODELO,
        "agentes": ["Triage", "Diagnóstico", "Tratamiento"],
        "cache": cache_manager.get_stats(),
        "endpoints": {
            "/consultar": "POST - Realizar consulta médica",
            "/estadisticas": "GET - Obtener estadísticas",
            "/consultas": "GET - Listar consultas",
            "/pacientes": "GET - Listar pacientes",
            "/web": "GET - Interfaz web",
            "/docs": "GET - Documentación Swagger",
            "/health": "GET - Health check"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Verifica el estado del sistema"""
    # Verificar Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        ollama_status = "connected" if response.status_code == 200 else "disconnected"
    except:
        ollama_status = "disconnected"
    
    # Verificar base de datos
    try:
        db.conn.execute("SELECT 1")
        db_status = "connected"
    except:
        db_status = "disconnected"
    
    # Estado general
    overall_status = "healthy" if ollama_status == "connected" and db_status == "connected" else "degraded"
    
    return HealthResponse(
        status=overall_status,
        ollama=ollama_status,
        modelo=MODELO,
        database=db_status,
        cache=cache_manager.get_stats()['type'],
        timestamp=datetime.now().isoformat()
    )

@app.post("/consultar", response_model=ConsultaResponse)
async def consultar(request: ConsultaRequest, background_tasks: BackgroundTasks):
    """
    Realiza una consulta médica usando el sistema multiagente
    
    - **sintomas**: Descripción de los síntomas del paciente
    - **nombre_paciente**: Nombre del paciente (opcional)
    - **edad**: Edad del paciente (opcional)
    """
    if not request.sintomas or len(request.sintomas.strip()) < 5:
        raise HTTPException(
            status_code=400, 
            detail="Describe tus síntomas con más detalle (mínimo 5 caracteres)"
        )
    
    inicio_total = time.time()
    from_cache = False
    
    try:
        # Verificar caché primero
        cached_result = await cache_manager.get_consulta(request.sintomas, request.edad)
        
        if cached_result:
            from_cache = True
            tiempo_total = 0.1  # Tiempo simbólico
            logger.info(f"✅ Consulta respondida desde caché: {request.sintomas[:50]}...")
            
            # Crear paciente en BD (para registro)
            paciente_id = db.crear_paciente(request.nombre_paciente, request.edad)
            
            # Guardar en BD (para historial)
            consulta_id = db.guardar_consulta({
                'paciente_id': paciente_id,
                'sintomas': request.sintomas,
                'triage': cached_result.get('triage', ''),
                'diagnostico': cached_result.get('diagnostico', ''),
                'tratamiento': cached_result.get('tratamiento', ''),
                'nivel_urgencia': cached_result.get('nivel_urgencia', ''),
                'tiempo_procesamiento': 0.1,
                'modelo_ia': MODELO
            })
            
            return ConsultaResponse(
                id=consulta_id,
                sintomas=request.sintomas,
                triage=cached_result.get('triage', ''),
                diagnostico=cached_result.get('diagnostico', ''),
                tratamiento=cached_result.get('tratamiento', ''),
                nivel_urgencia=cached_result.get('nivel_urgencia', 'NO_CLASIFICADO'),
                tiempo_procesamiento=0.1,
                from_cache=True,
                timestamp=datetime.now().isoformat()
            )
        
        # Crear paciente
        paciente_id = db.crear_paciente(request.nombre_paciente, request.edad)
        
        # Ejecutar multiagente
        resultados = await ejecutar_multiagente(request.sintomas)
        tiempo_total = time.time() - inicio_total
        
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
        
        logger.info(f"✅ Consulta {consulta_id} completada en {tiempo_total:.1f}s")
        
        return ConsultaResponse(
            id=consulta_id,
            sintomas=request.sintomas,
            triage=resultados['triage'],
            diagnostico=resultados['diagnostico'],
            tratamiento=resultados['tratamiento'],
            nivel_urgencia=resultados['nivel_urgencia'],
            tiempo_procesamiento=tiempo_total,
            from_cache=False,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en consulta: {e}")
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
    limite = min(limite, 50)
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
    
    logger.info(f"Consulta {consulta_id} eliminada")
    return {"message": f"Consulta {consulta_id} eliminada", "success": True}

@app.delete("/cache")
async def limpiar_cache():
    """Limpia toda la caché del sistema"""
    await cache_manager.clear_all()
    logger.info("Caché limpiada completamente")
    return {"message": "Caché limpiada correctamente", "success": True}

@app.get("/cache/stats")
async def cache_stats():
    """Obtiene estadísticas de la caché"""
    return cache_manager.get_stats()

# ============================================
# INTERFAZ WEB MEJORADA
# ============================================

HTML_WEB = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema Multiagente Médico | IA para Diagnóstico</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        .header p {
            opacity: 0.9;
        }
        
        .content {
            padding: 30px;
        }
        
        .info-agentes {
            display: flex;
            justify-content: space-around;
            margin-bottom: 30px;
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .agente-card {
            background: #f8f9fa;
            padding: 15px 20px;
            border-radius: 15px;
            text-align: center;
            flex: 1;
            min-width: 100px;
            transition: transform 0.3s;
        }
        
        .agente-card:hover {
            transform: translateY(-5px);
        }
        
        .agente-icon {
            font-size: 2em;
            margin-bottom: 8px;
        }
        
        .agente-nombre {
            font-weight: bold;
            color: #333;
        }
        
        .agente-desc {
            font-size: 0.8em;
            color: #666;
            margin-top: 5px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #333;
        }
        
        textarea, input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 14px;
            transition: border-color 0.3s;
            font-family: inherit;
        }
        
        textarea:focus, input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        textarea {
            resize: vertical;
            min-height: 120px;
        }
        
        .row {
            display: flex;
            gap: 15px;
        }
        
        .row > div {
            flex: 1;
        }
        
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .loading {
            text-align: center;
            padding: 30px;
            display: none;
        }
        
        .spinner {
            width: 50px;
            height: 50px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .resultado {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 15px;
            display: none;
            animation: fadeIn 0.5s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .result-card {
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 10px;
            border-left: 4px solid;
        }
        
        .result-card.triage { border-left-color: #dc3545; }
        .result-card.diagnostico { border-left-color: #28a745; }
        .result-card.tratamiento { border-left-color: #17a2b8; }
        
        .result-card h4 {
            margin-bottom: 8px;
            color: #333;
        }
        
        .result-card p {
            color: #666;
            line-height: 1.5;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            margin-top: 10px;
        }
        
        .badge-cache {
            background: #17a2b8;
            color: white;
        }
        
        .tiempo {
            text-align: center;
            margin-top: 15px;
            color: #666;
            font-size: 14px;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 12px;
            border-radius: 8px;
            margin-top: 15px;
            display: none;
        }
        
        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 12px;
            border-top: 1px solid #e0e0e0;
        }
        
        @media (max-width: 600px) {
            .row { flex-direction: column; gap: 10px; }
            .info-agentes { flex-direction: column; }
            .content { padding: 20px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 Sistema Multiagente Médico</h1>
            <p>Inteligencia Artificial para Triage, Diagnóstico y Tratamiento</p>
        </div>
        
        <div class="content">
            <div class="info-agentes">
                <div class="agente-card">
                    <div class="agente-icon">🟡</div>
                    <div class="agente-nombre">TRIAGE</div>
                    <div class="agente-desc">Clasifica urgencia</div>
                </div>
                <div class="agente-card">
                    <div class="agente-icon">🔵</div>
                    <div class="agente-nombre">DIAGNÓSTICO</div>
                    <div class="agente-desc">Identifica condición</div>
                </div>
                <div class="agente-card">
                    <div class="agente-icon">🟢</div>
                    <div class="agente-nombre">TRATAMIENTO</div>
                    <div class="agente-desc">Recomienda acciones</div>
                </div>
            </div>
            
            <form id="consultaForm">
                <div class="form-group">
                    <label>🩺 Describe tus síntomas</label>
                    <textarea id="sintomas" placeholder="Ej: Tengo dolor de cabeza intenso, mareos y náuseas desde hace 2 días"></textarea>
                </div>
                
                <div class="row">
                    <div class="form-group">
                        <label>👤 Tu nombre (opcional)</label>
                        <input type="text" id="nombre" placeholder="Nombre">
                    </div>
                    <div class="form-group">
                        <label>📊 Edad (opcional)</label>
                        <input type="number" id="edad" placeholder="Años">
                    </div>
                </div>
                
                <button type="submit" id="consultarBtn">🔍 Realizar Consulta Médica</button>
            </form>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <div>🤖 Procesando con 3 agentes IA...</div>
                <div style="font-size: 12px; margin-top: 10px;">Triage → Diagnóstico → Tratamiento</div>
                <div style="font-size: 11px; color: #999; margin-top: 5;">Esto puede tomar 30-45 segundos</div>
            </div>
            
            <div class="error" id="error"></div>
            
            <div class="resultado" id="resultado">
                <h3 style="margin-bottom: 15px;">📊 Resultados del Sistema Multiagente</h3>
                <div class="result-card triage" id="triage"></div>
                <div class="result-card diagnostico" id="diagnostico"></div>
                <div class="result-card tratamiento" id="tratamiento"></div>
                <div class="tiempo" id="tiempo"></div>
            </div>
        </div>
        
        <div class="footer">
            ⚡ Utiliza IA local con Ollama (phi3) | 🔒 Privacidad garantizada | 💾 Consultas guardadas
        </div>
    </div>
    
    <script>
        const form = document.getElementById('consultaForm');
        const sintomasInput = document.getElementById('sintomas');
        const nombreInput = document.getElementById('nombre');
        const edadInput = document.getElementById('edad');
        const consultarBtn = document.getElementById('consultarBtn');
        const loading = document.getElementById('loading');
        const resultado = document.getElementById('resultado');
        const error = document.getElementById('error');
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const sintomas = sintomasInput.value.trim();
            if (!sintomas) {
                mostrarError('Por favor describe tus síntomas');
                return;
            }
            
            if (sintomas.length < 5) {
                mostrarError('Describe tus síntomas con más detalle');
                return;
            }
            
            ocultarError();
            loading.style.display = 'block';
            resultado.style.display = 'none';
            consultarBtn.disabled = true;
            
            try {
                const startTime = Date.now();
                
                const response = await fetch('/consultar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        sintomas: sintomas,
                        nombre_paciente: nombreInput.value.trim() || null,
                        edad: parseInt(edadInput.value) || 0
                    })
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Error en la consulta');
                }
                
                const data = await response.json();
                const endTime = Date.now();
                const tiempo = ((endTime - startTime) / 1000).toFixed(1);
                
                document.getElementById('triage').innerHTML = `
                    <h4>🔴 TRIAGE</h4>
                    <p>${data.triage || 'No disponible'}</p>
                `;
                document.getElementById('diagnostico').innerHTML = `
                    <h4>🩺 DIAGNÓSTICO</h4>
                    <p>${data.diagnostico || 'No disponible'}</p>
                `;
                document.getElementById('tratamiento').innerHTML = `
                    <h4>💊 TRATAMIENTO</h4>
                    <p>${data.tratamiento || 'No disponible'}</p>
                `;
                
                let tiempoHtml = `⏱️ Tiempo total: ${tiempo} segundos`;
                if (data.from_cache) {
                    tiempoHtml += ' <span class="badge badge-cache">⚡ Desde caché</span>';
                }
                document.getElementById('tiempo').innerHTML = tiempoHtml;
                
                resultado.style.display = 'block';
                
            } catch (err) {
                mostrarError(err.message);
            } finally {
                loading.style.display = 'none';
                consultarBtn.disabled = false;
            }
        });
        
        function mostrarError(mensaje) {
            error.textContent = mensaje;
            error.style.display = 'block';
            setTimeout(() => {
                error.style.display = 'none';
            }, 5000);
        }
        
        function ocultarError() {
            error.style.display = 'none';
        }
        
        // Ctrl+Enter para enviar
        sintomasInput.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                form.dispatchEvent(new Event('submit'));
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
        host=settings.API_HOST, 
        port=settings.API_PORT, 
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )