# src/config/settings.py
"""Configuración centralizada del sistema"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    """Configuración global de la aplicación"""
    
    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_VERSION: str = "3.0.0"
    API_TITLE: str = "Sistema Multiagente Médico API"
    API_DESCRIPTION: str = "API profesional para consultas médicas con IA multiagente"
    
    # Base de datos
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "datos/consultas.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "")
    
    # Seguridad
    SECRET_KEY: str = os.getenv("SECRET_KEY", "cambia-esta-clave-por-una-segura-en-produccion")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Ollama
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "phi3:latest")
    MODEL_TIMEOUT: int = int(os.getenv("MODEL_TIMEOUT", "45"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "80"))
    
    # Rate limiting
    RATE_LIMIT_CALLS: int = int(os.getenv("RATE_LIMIT_CALLS", "10"))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", "60"))
    
    # Caché
    CACHE_TTL_DEFAULT: int = 3600
    CACHE_TTL_URGENTE: int = 300
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()