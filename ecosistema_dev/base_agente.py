from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate

class NexusBaseAgent:
    """Clase maestra para todos los agentes del ecosistema Nexus."""
    
    def __init__(self, nombre, especialidad, instrucciones_sistema, modelo="tinyllama"):
        self.nombre = nombre
        self.especialidad = especialidad
        
        # Inicializamos el motor Ollama
        print(f"[NEXUS-BASE] Inicializando agente {nombre} con modelo {modelo}...")
        try:
            self.llm = Ollama(model=modelo)
        except Exception as e:
            print(f"[ERROR] No se pudo conectar con Ollama: {e}")
            self.llm = None

        # Definimos la plantilla de prompt (Personalidad del Agente)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", f"Eres el Agente {nombre}, especialista en {especialidad}. {instrucciones_sistema}"),
            ("user", "{entrada}")
        ])
        
        # Creamos la cadena (Chain)
        if self.llm:
            self.chain = self.prompt | self.llm
        else:
            self.chain = None

    def responder(self, mensaje_usuario):
        if not self.chain:
            return "Error: Motor LLM no disponible. Verifica que Ollama esté corriendo."
        
        print(f"[{self.nombre}] Procesando petición...")
        return self.chain.invoke({"entrada": mensaje_usuario})

    def registrar_herramienta(self, nombre_tool, funcion_tool):
        """Método para añadir capacidades técnicas (ML/DL) en el futuro."""
        # En fases posteriores usaremos LangChain Tools & Agents
        pass
