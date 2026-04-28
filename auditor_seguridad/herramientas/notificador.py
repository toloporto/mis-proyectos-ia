from crewai.tools import tool
import os

@tool("Enviar Alerta de Seguridad")
def enviar_alerta(mensaje: str) -> str:
    """
    Envía una notificación visual al escritorio de Linux y hace un pitido.
    Útil cuando se detecta una amenaza crítica que requiere atención inmediata.
    """
    # Enviar notificación visual al escritorio
    os.system(f'notify-send "🚨 ALERTA DE SEGURIDAD" "{mensaje}"')
    
    # Intentar hacer un sonido de sistema (pitido)
    os.system('echo -e "\a"') 
    
    return f"Notificación enviada con éxito: {mensaje}"