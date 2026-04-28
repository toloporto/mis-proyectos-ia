# 🛡️ IA Auditor de Seguridad Híbrido

Sistema avanzado de auditoría basado en Agentes de IA (**CrewAI** + **Llama 3.1**) diseñado para monitorizar logs, investigar amenazas en la red y analizar la integridad de archivos sospechosos.

## 🚀 Capacidades Actuales
- **Monitorización de Logs:** Analiza registros de servidor en busca de patrones de ataque (Fuerza Bruta, Errores Críticos).
- **Investigación de Red:** Ante una IP sospechosa, el agente realiza una búsqueda activa en internet para verificar su reputación.
- **Análisis de Malware:** Genera huellas digitales (SHA-256) de archivos sospechosos en la zona de cuarentena.
- **Alertas Proactivas:** Envía notificaciones de escritorio inmediatas al detectar una amenaza confirmada.

## 📁 Estructura del Proyecto
- `src/main.py`: Cerebro y orquestador del agente.
- `herramientas/`:
    - `lector.py`: Acceso al sistema de archivos para lectura de logs.
    - `notificador.py`: Conexión con el sistema de avisos de Linux.
    - `buscador.py`: Integración con DuckDuckGo para inteligencia de red.
    - `analizador_archivos.py`: Generador de hashes para archivos sospechosos.
- `datos/`: Carpeta de logs de servidor.
- `buzon_sospechoso/`: Zona de cuarentena para análisis de archivos.

## 🛠️ Requisitos e Instalación
1. **Ollama:** Tener instalado y corriendo Llama 3.1 (`ollama run llama3.1`).
2. **Entorno:** `source .venv/bin/activate`
3. **Librerías:** `pip install crewai duckduckgo-search ddgs libnotify-bin` (este último vía apt).

## 🧑‍💻 Uso
Para iniciar el sistema de defensa:
```bash
python3 src/main.py