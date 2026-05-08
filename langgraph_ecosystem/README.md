# LangGraph Multi-Agent Ecosystem

¡Bienvenido al **LangGraph Multi-Agent Ecosystem**! Este proyecto es una aplicación web impulsada por Inteligencia Artificial que implementa una arquitectura multi-agente basada en **LangGraph** y **LangChain**. Sirve de entorno de prueba para la coordinación y ejecución de tareas complejas utilizando agentes especializados.

## 🚀 Características Principales
- **Arquitectura Multi-Agente**: Orquestación de diferentes agentes utilizando `LangGraph` para crear flujos de trabajo avanzados.
- **Backend con FastAPI**: Servidor web rápido y moderno que expone una API REST para interactuar con el ecosistema de IA a través del endpoint `/chat`.
- **Interfaz Web Integrada**: Cliente web estático (HTML, CSS y JS) disponible desde la raíz (`/`) para interactuar con los agentes de manera visual y directa.
- **Gestión de Memoria y Estado**: Rastreo del hilo conversacional (`thread_id`) y resultados intermedios usando las capacidades de LangGraph.

## 📁 Estructura del Proyecto

```text
langgraph_ecosystem/
├── app/
│   ├── agents/        # Definición de los agentes (supervisor, workers, etc.)
│   ├── core/          # Lógica central del sistema y definición del grafo de LangGraph
│   ├── memory/        # Componentes para guardar el estado y contexto
│   ├── ml/            # Modelos de Machine Learning y conectores (PyTorch, LLMs)
│   ├── static/        # Frontend: Interfaz web, JS y estilos CSS
│   ├── utils/         # Utilidades y funciones de soporte
│   └── main.py        # Archivo principal de la aplicación FastAPI
├── data/              # Bases de datos y almacenamiento (e.g. vector databases)
├── notebooks/         # Cuadernos de Jupyter para experimentación
├── scripts/           # Scripts auxiliares para el proyecto
├── tests/             # Batería de tests unitarios y de integración
├── Makefile           # Comandos de utilidad (ej. inicio rápido, formateo)
└── requirements.txt   # Dependencias de Python del proyecto
```

## 🛠️ Instalación y Uso

### 1. Entorno Virtual
Se recomienda utilizar un entorno virtual para aislar las dependencias:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar Dependencias
Una vez activado el entorno, instala los paquetes necesarios:
```bash
pip install -r requirements.txt
```

### 3. Ejecutar el Servidor
Inicia la aplicación FastAPI utilizando `uvicorn`:
```bash
uvicorn app.main:api --reload
```
La aplicación estará disponible en `http://localhost:8000`.

## 🤖 Cómo interactuar con los Agentes
1. **Vía Interfaz Web:** Abre tu navegador en `http://localhost:8000` para usar la interfaz de chat gráfica.
2. **Vía API REST:** Puedes enviar peticiones POST al endpoint de chat para integrarlo con otros sistemas.
```bash
curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"user_input": "Hola, ¿cómo estás?", "thread_id": "mi_sesion_1"}'
```

## 🧪 Pruebas
El proyecto incluye un entorno de testing. Para ejecutar las pruebas de validación de los agentes y de la API, ejecuta:
```bash
pytest
```
*(Puedes verificar los archivos `test_app.py` y `test_mock.py` para más detalles).*

---
*Este proyecto es parte del entorno de desarrollo local e investigación en orquestación de sistemas de IA multi-agente.*
