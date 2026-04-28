# src/utils/logger.py
"""Sistema de logging profesional"""

import logging
import sys
from pathlib import Path
from datetime import datetime
import os

# Crear directorio de logs si no existe
Path("logs").mkdir(exist_ok=True)

def setup_logger(name: str = "sistema_medico") -> logging.Logger:
    """Configura logger con múltiples handlers"""
    
    logger = logging.getLogger(name)
    
    # Evitar duplicación de handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    
    # Formato para logs
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo
    try:
        file_handler = logging.FileHandler(
            f"logs/{name}_{datetime.now().strftime('%Y%m%d')}.log",
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception:
        pass
    
    return logger

# Logger global
logger = setup_logger()

def get_logger(name: str = None):
    """Obtiene un logger configurado"""
    if name:
        return setup_logger(name)
    return logger