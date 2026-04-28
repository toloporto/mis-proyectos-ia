# src/database/database.py
# BASE DE DATOS SQLITE PARA CONSULTAS MULTIAGENTE

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any
import os

DB_PATH = "/home/toloporto/proyectos/langGraph-Telemedicina/datos/consultas.db"

class Database:
    def __init__(self):
        self.conn = None
        self.init_db()
    
    def init_db(self):
        """Inicializa la base de datos con todas las tablas necesarias"""
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        
        # Tabla de pacientes
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS pacientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                edad INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de consultas multiagente
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS consultas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER,
                sintomas TEXT NOT NULL,
                triage TEXT,
                diagnostico TEXT,
                tratamiento TEXT,
                nivel_urgencia TEXT,
                tiempo_procesamiento REAL,
                modelo_ia TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
            )
        ''')
        
        # Tabla de historial de agentes (cada agente individual)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS agentes_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                consulta_id INTEGER,
                agente_nombre TEXT,
                agente_respuesta TEXT,
                tiempo_ejecucion REAL,
                orden INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (consulta_id) REFERENCES consultas(id)
            )
        ''')
        
        # Tabla de métricas del sistema
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS metricas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATE,
                total_consultas INTEGER,
                tiempo_promedio REAL,
                modelo_principal TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        print("✅ Base de datos inicializada correctamente")
    
    def crear_paciente(self, nombre: str = None, edad: int = 0) -> int:
        """Crea un nuevo paciente y retorna su ID"""
        cursor = self.conn.execute(
            "INSERT INTO pacientes (nombre, edad) VALUES (?, ?)",
            (nombre or f"Paciente_{datetime.now().strftime('%Y%m%d%H%M%S')}", edad)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def guardar_consulta(self, consulta_data: Dict[str, Any]) -> int:
        """Guarda una consulta multiagente completa"""
        cursor = self.conn.execute('''
            INSERT INTO consultas (
                paciente_id, sintomas, triage, diagnostico, tratamiento,
                nivel_urgencia, tiempo_procesamiento, modelo_ia
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            consulta_data.get('paciente_id'),
            consulta_data.get('sintomas'),
            consulta_data.get('triage'),
            consulta_data.get('diagnostico'),
            consulta_data.get('tratamiento'),
            consulta_data.get('nivel_urgencia'),
            consulta_data.get('tiempo_procesamiento'),
            consulta_data.get('modelo_ia')
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def guardar_agente_log(self, log_data: Dict[str, Any]):
        """Guarda el log de cada agente individual"""
        self.conn.execute('''
            INSERT INTO agentes_log (
                consulta_id, agente_nombre, agente_respuesta, 
                tiempo_ejecucion, orden
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            log_data.get('consulta_id'),
            log_data.get('agente_nombre'),
            log_data.get('agente_respuesta'),
            log_data.get('tiempo_ejecucion'),
            log_data.get('orden')
        ))
        self.conn.commit()
    
    def obtener_consultas(self, limite: int = 10) -> List[Dict]:
        """Obtiene las últimas consultas"""
        cursor = self.conn.execute('''
            SELECT c.*, p.nombre as paciente_nombre
            FROM consultas c
            LEFT JOIN pacientes p ON c.paciente_id = p.id
            ORDER BY c.created_at DESC
            LIMIT ?
        ''', (limite,))
        return [dict(row) for row in cursor.fetchall()]
    
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas del sistema"""
        cursor = self.conn.execute('''
            SELECT 
                COUNT(*) as total_consultas,
                AVG(tiempo_procesamiento) as tiempo_promedio,
                COUNT(DISTINCT paciente_id) as total_pacientes
            FROM consultas
        ''')
        stats = dict(cursor.fetchone())
        
        cursor = self.conn.execute('''
            SELECT nivel_urgencia, COUNT(*) as cantidad
            FROM consultas
            GROUP BY nivel_urgencia
        ''')
        stats['urgencias'] = [dict(row) for row in cursor.fetchall()]
        
        return stats
    
    def obtener_consultas_por_fecha(self, fecha_inicio: str, fecha_fin: str) -> List[Dict]:
        """Obtiene consultas en un rango de fechas"""
        cursor = self.conn.execute('''
            SELECT * FROM consultas
            WHERE DATE(created_at) BETWEEN ? AND ?
            ORDER BY created_at DESC
        ''', (fecha_inicio, fecha_fin))
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.conn:
            self.conn.close()

# Instancia global
db = Database()
