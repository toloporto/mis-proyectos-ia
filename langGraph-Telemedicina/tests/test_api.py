# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.api import app

client = TestClient(app)

def test_root_endpoint():
    """Test del endpoint raíz"""
    response = client.get("/")
    assert response.status_code == 200
    assert "api" in response.json()
    assert "version" in response.json()

def test_health_endpoint():
    """Test del health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_consultar_endpoint_validation():
    """Test validación de síntomas vacíos"""
    response = client.post("/consultar", json={
        "sintomas": "",
        "edad": 30
    })
    assert response.status_code == 400
    assert "detail" in response.json()

def test_consultar_endpoint_sintomas_cortos():
    """Test síntomas muy cortos"""
    response = client.post("/consultar", json={
        "sintomas": "a",
        "edad": 30
    })
    assert response.status_code == 400

def test_cache_endpoint():
    """Test endpoint de estadísticas de caché"""
    response = client.get("/cache/stats")
    assert response.status_code == 200
    assert "type" in response.json()
    assert "keys" in response.json()

def test_estadisticas_endpoint():
    """Test endpoint de estadísticas"""
    response = client.get("/estadisticas")
    assert response.status_code == 200
    assert "total_consultas" in response.json()

def test_consultas_endpoint():
    """Test listado de consultas"""
    response = client.get("/consultas")
    assert response.status_code == 200
    assert "consultas" in response.json()

def test_pacientes_endpoint():
    """Test listado de pacientes"""
    response = client.get("/pacientes")
    assert response.status_code == 200
    assert "pacientes" in response.json()

@pytest.mark.slow
def test_consultar_real():
    """Test consulta real (puede ser lenta)"""
    response = client.post("/consultar", json={
        "sintomas": "dolor de cabeza",
        "edad": 30
    })
    assert response.status_code == 200
    assert "triage" in response.json()
    assert "diagnostico" in response.json()
