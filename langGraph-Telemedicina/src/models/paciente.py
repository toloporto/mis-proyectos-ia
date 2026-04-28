from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Paciente:
    id: str
    nombre: str
    edad: int
    sintomas: List[str]
    urgencia: Optional[str] = None
    fecha_registro: datetime = datetime.now()
    
    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "edad": self.edad,
            "sintomas": self.sintomas,
            "urgencia": self.urgencia
        }