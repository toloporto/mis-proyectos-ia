import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODELO_DEFAULT = "gpt-3.5-turbo"
    TEMPERATURA_DEFAULT = 0.3
    
    # Configuración médica
    SINTOMAS_URGENTES = ["dolor pecho", "dificultad respirar", "sangrado", "desmayo"]
    HORARIO_CONSULTAS = "9:00-18:00"
    
    @classmethod
    def validar_api_key(cls):
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY no encontrada en .env")