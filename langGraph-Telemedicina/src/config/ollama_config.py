# src/config/ollama_config.py
"""Configuración y optimización de Ollama"""

import subprocess
import json
import requests
from typing import Dict, Any, Optional
from .settings import settings

class OllamaOptimizer:
    """Optimizador de rendimiento para Ollama"""
    
    @staticmethod
    def get_available_models() -> list:
        """Obtiene lista de modelos disponibles en Ollama"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [m["name"] for m in models]
            return []
        except:
            return []
    
    @staticmethod
    def set_parallel_requests(limit: int = 2):
        """Configura límite de requests paralelos"""
        try:
            subprocess.run(["ollama", "set", "parallel", str(limit)], check=True)
            return {"status": "ok", "parallel_requests": limit}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def get_performance_metrics() -> Dict[str, Any]:
        """Obtiene métricas de rendimiento de Ollama"""
        try:
            # Verificar estado
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code != 200:
                return {"status": "error", "message": "Ollama no responde"}
            
            models = response.json().get("models", [])
            
            return {
                "status": "ok",
                "models_available": len(models),
                "models_list": [m["name"] for m in models[:5]],  # Solo primeros 5
                "default_model": settings.DEFAULT_MODEL,
                "timeout": settings.MODEL_TIMEOUT
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def optimize_for_medicine() -> Dict[str, Any]:
        """Configuración optimizada para consultas médicas"""
        config = {
            "num_ctx": 2048,           # Contexto aumentado
            "num_gpu": 1,               # Usar GPU si está disponible
            "temperature": 0.2,         # Baja temperatura para consistencia
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.1,
            "stop": ["</s>", "Human:", "User:"]
        }
        
        return {
            "status": "ok",
            "config": config,
            "recommended_model": settings.DEFAULT_MODEL
        }
