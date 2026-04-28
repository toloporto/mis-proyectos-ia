# src/cache/cache_manager.py
"""Sistema de caché simple en memoria"""

import json
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import sys
import os

# Configurar path para importaciones
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config.settings import settings
except ImportError:
    from src.config.settings import settings

class CacheManager:
    """Gestor de caché en memoria"""
    
    def __init__(self):
        self._cache: Dict[str, Dict] = {}
    
    def _get_key(self, prefix: str, *args) -> str:
        """Genera clave única para caché"""
        data = "|".join(str(arg) for arg in args)
        return f"{prefix}:{hashlib.md5(data.encode()).hexdigest()}"
    
    def _get_ttl(self, nivel_urgencia: str = "") -> int:
        """Determina TTL basado en nivel de urgencia"""
        if "EMERGENCIA" in nivel_urgencia or "GRAVE" in nivel_urgencia:
            return settings.CACHE_TTL_URGENTE
        return settings.CACHE_TTL_DEFAULT
    
    def get(self, key: str) -> Optional[Dict]:
        """Obtiene valor del caché (método síncrono)"""
        item = self._cache.get(key)
        if item and datetime.now() < item["expires"]:
            return item["data"]
        return None
    
    def set(self, key: str, value: Dict, ttl: int = None):
        """Guarda valor en caché"""
        if ttl is None:
            ttl = settings.CACHE_TTL_DEFAULT
        self._cache[key] = {
            "data": value,
            "expires": datetime.now() + timedelta(seconds=ttl)
        }
    
    def delete(self, key: str):
        """Elimina clave del caché"""
        self._cache.pop(key, None)
    
    def clear(self):
        """Limpia todo el caché"""
        self._cache.clear()
    
    def get_consulta(self, sintomas: str, edad: int = 0) -> Optional[Dict]:
        """Obtiene consulta del caché"""
        key = self._get_key("consulta", sintomas.lower().strip(), edad)
        return self.get(key)
    
    def set_consulta(self, sintomas: str, edad: int, resultado: Dict):
        """Guarda consulta en caché"""
        key = self._get_key("consulta", sintomas.lower().strip(), edad)
        ttl = self._get_ttl(resultado.get('nivel_urgencia', ''))
        self.set(key, resultado, ttl)
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas del caché"""
        return {
            "type": "memory",
            "keys": len(self._cache),
            "status": "ok"
        }

# Instancia global
cache_manager = CacheManager()