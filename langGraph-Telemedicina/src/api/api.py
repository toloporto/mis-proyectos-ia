# src/api/api.py
"""
API FastAPI v3.0 — Sistema Multiagente Médico
- Sirve el frontend desde web-client/
- Endpoints limpios con documentación automática
- Soporte para Server-Sent Events (streaming por agente)
- Sin HTML embebido
"""

import time
import sys
import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from cache.cache_manager import cache_manager
from utils.logger import logger
from agents.sistema_phi3_db import consultar, db

# ============================================================
# CONFIGURACIÓN FASTAPI
# ============================================================

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos del frontend
FRONTEND_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "web-client",
)

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# ============================================================
# MODELOS PYDANTIC
# ============================================================

class ConsultaRequest(BaseModel):
    sintomas: str
    nombre_paciente: Optional[str] = None
    edad: Optional[int] = 0

    class Config:
        json_schema_extra = {
            "example": {
                "sintomas": "Dolor de cabeza intenso, mareos y náuseas desde hace 2 días",
                "nombre_paciente": "Ana García",
                "edad": 35,
            }
        }


class ConsultaResponse(BaseModel):
    triage: str
    diagnostico: str
    tratamiento: str
    nivel_urgencia: str
    protocolo: str
    tiempo_procesamiento: float
    from_cache: bool
    modelo: str


# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/", include_in_schema=False)
async def raiz():
    """Sirve el frontend."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"mensaje": "API funcionando. Docs en /docs"})


@app.get("/health")
async def health_check():
    """Estado del sistema."""
    import requests as req
    try:
        r = req.get("http://localhost:11434/api/tags", timeout=3)
        ollama_ok = r.status_code == 200
        modelos = [m["name"] for m in r.json().get("models", [])] if ollama_ok else []
    except Exception:
        ollama_ok = False
        modelos = []

    return {
        "status": "ok",
        "api_version": settings.API_VERSION,
        "ollama": "conectado" if ollama_ok else "desconectado",
        "modelo_activo": settings.DEFAULT_MODEL,
        "modelos_disponibles": modelos,
        "cache": cache_manager.get_stats(),
    }


@app.post("/consultar", response_model=ConsultaResponse)
async def realizar_consulta(request: ConsultaRequest):
    """
    Realiza una consulta médica multiagente.

    El sistema ejecuta:
    1. **Triage** — clasifica la urgencia
    2. **Diagnóstico ∥ Tratamiento** — en paralelo (si no es EMERGENCIA ni LEVE)

    O bien activa protocolos específicos para EMERGENCIA o síntomas LEVE.
    """
    if not request.sintomas or len(request.sintomas.strip()) < 5:
        raise HTTPException(
            status_code=422,
            detail="Describe tus síntomas con al menos 5 caracteres.",
        )

    logger.info(
        f"Nueva consulta: '{request.sintomas[:60]}...' | "
        f"Paciente: {request.nombre_paciente or 'anónimo'} | Edad: {request.edad}"
    )

    resultado = consultar(
        sintomas=request.sintomas.strip(),
        nombre=request.nombre_paciente or "",
        edad=request.edad or 0,
    )

    if not resultado:
        raise HTTPException(
            status_code=503,
            detail="El sistema de IA no está disponible. Verifica que Ollama está corriendo.",
        )

    return ConsultaResponse(
        triage=resultado.get("triage", "No disponible"),
        diagnostico=resultado.get("diagnostico", "No disponible"),
        tratamiento=resultado.get("tratamiento", "No disponible"),
        nivel_urgencia=resultado.get("nivel_urgencia", "MODERADO"),
        protocolo=resultado.get("protocolo", "normal"),
        tiempo_procesamiento=round(resultado.get("tiempo_procesamiento", 0), 2),
        from_cache=resultado.get("from_cache", False),
        modelo=settings.DEFAULT_MODEL,
    )


@app.get("/historial")
async def obtener_historial(limite: int = 10):
    """Devuelve las últimas N consultas registradas."""
    if limite > 50:
        limite = 50
    consultas = db.obtener_consultas(limite)
    return {"total": len(consultas), "consultas": consultas}


@app.get("/estadisticas")
async def estadisticas():
    """Estadísticas generales del sistema."""
    cache_stats = cache_manager.get_stats()

    try:
        import sqlite3
        with sqlite3.connect(settings.DATABASE_PATH) as conn:
            conn.row_factory = sqlite3.Row
            total = conn.execute("SELECT COUNT(*) as n FROM consultas").fetchone()["n"]
            por_nivel = conn.execute(
                "SELECT nivel_urgencia, COUNT(*) as n FROM consultas GROUP BY nivel_urgencia"
            ).fetchall()
            por_protocolo = conn.execute(
                "SELECT protocolo, COUNT(*) as n FROM consultas GROUP BY protocolo"
            ).fetchall()
            tiempo_medio = conn.execute(
                "SELECT AVG(tiempo_procesamiento) as avg FROM consultas WHERE from_cache = 0"
            ).fetchone()["avg"]
    except Exception:
        total, por_nivel, por_protocolo, tiempo_medio = 0, [], [], 0

    return {
        "consultas_totales": total,
        "tiempo_medio_segundos": round(tiempo_medio or 0, 2),
        "por_nivel_urgencia": [dict(r) for r in por_nivel],
        "por_protocolo": [dict(r) for r in por_protocolo],
        "cache": cache_stats,
    }


@app.delete("/cache")
async def limpiar_cache():
    """Limpia el caché en memoria."""
    cache_manager.clear()
    logger.info("Caché limpiado manualmente vía API")
    return {"mensaje": "Caché limpiado correctamente"}


# ============================================================
# PUNTO DE ENTRADA
# ============================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
    )
