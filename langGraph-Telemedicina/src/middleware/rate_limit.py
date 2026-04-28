# src/middleware/rate_limit.py
"""Middleware para limitar requests por IP"""

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
import time
from typing import Dict, List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config.settings import settings
except ImportError:
    from src.config.settings import settings

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware que limita el número de requests por IP"""
    
    def __init__(self, app):
        super().__init__(app)
        self.calls = settings.RATE_LIMIT_CALLS
        self.period = settings.RATE_LIMIT_PERIOD
        self.requests: Dict[str, List[float]] = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        # Excluir endpoints de documentación y health check
        if request.url.path in ["/docs", "/redoc", "/openapi.json", "/health"]:
            return await call_next(request)
        
        client_ip = request.client.host
        now = time.time()
        
        # Limpiar requests antiguas
        self.requests[client_ip] = [
            timestamp for timestamp in self.requests[client_ip]
            if now - timestamp < self.period
        ]
        
        # Verificar límite
        if len(self.requests[client_ip]) >= self.calls:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Límite de {self.calls} requests cada {self.period} segundos excedido",
                    "retry_after": int(self.period - (now - self.requests[client_ip][0]))
                }
            )
        
        self.requests[client_ip].append(now)
        response = await call_next(request)
        
        # Añadir headers de rate limit
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(self.calls - len(self.requests[client_ip]))
        response.headers["X-RateLimit-Reset"] = str(int(now + self.period))
        
        return response