from crewai.tools import tool
import ctypes

@tool("Enviar Alerta de Seguridad")
def enviar_alerta(mensaje: str) -> str:
    """
    Envía una notificación visual al escritorio de Windows y hace un pitido.
    Útil cuando se detecta una amenaza crítica que requiere atención inmediata.
    """
    print(f"\a") # Sonido de sistema (pitido) en la consola
    
    # MB_ICONINFORMATION = 0x40, MB_OK = 0x0
    ctypes.windll.user32.MessageBoxW(0, mensaje, "🚨 ALERTA DE SEGURIDAD", 0x40 | 0x0)
    
    return f"Notificación enviada con éxito: {mensaje}"