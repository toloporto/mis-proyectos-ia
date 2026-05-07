# 🌌 Nexus AI Hub: Ecosistema Multi-Agente (v5.1)

Nexus es una plataforma avanzada de orquestación de IA diseñada para el análisis crítico en tiempo real. Utiliza una arquitectura de grafos persistentes (LangGraph) para coordinar múltiples agentes especializados en medicina, finanzas, seguros y farmacia.

## 🏗️ Arquitectura del Sistema

El ecosistema se divide en tres capas:
1.  **Capa de Orquestación:** `orquestador.py` + `grafo_nexus.py`. Maneja el flujo de decisiones y la memoria persistente.
2.  **Capa de Agentes Especialistas:** 
    -   `servidor_agente.py`: Médico (Computer Vision + ML).
    -   `agente_financiero.py`: Análisis de Riesgo Crediticio.
    -   `agente_seguros.py`: Evaluación de Pólizas.
    -   `agente_farmacia.py`: Recomendación de Tratamiento.
3.  **Capa de Interfaz:** `index.html`. Dashboard dinámico con monitores de inteligencia en tiempo real.

---

## 🚀 Guía de Lanzamiento Rápido

Para iniciar el ecosistema completo, asegúrate de tener activado el entorno virtual (`source venv_ia/bin/activate`) y ejecuta los siguientes comandos en terminales separadas:

### 1. Iniciar Agentes Especialistas
```bash
python servidor_agente.py    # Puerto 5000 (Médico)
python agente_financiero.py  # Puerto 5001 (Financiero)
python agente_seguros.py     # Puerto 5002 (Seguros)
python agente_farmacia.py    # Puerto 5003 (Farmacia)
```

### 2. Iniciar el Cerebro (Orquestador)
```bash
python orquestador.py        # Puerto 8000 (LangGraph Core)
```

### 3. Iniciar Interfaz de Usuario
```bash
python3 -m http.server 8080  # Dashboard Web
```
Accede a: `http://localhost:8080`

---

## 🧠 Capacidades Clave implementadas (2026 Ready)

-   💾 **Persistencia SQLite:** Cada conversación se guarda automáticamente en `nexus_memory.db`.
-   🧬 **Visión Multimodal:** Análisis de radiografías mediante redes neuronales convolucionales (DL).
-   🤖 **NER Robusto:** Extracción automática de datos mediante modelos Llama 3.2 y rescate por Regex avanzado.
-   📜 **Gestión de Historial:** Capacidad de recuperar y navegar entre sesiones de consulta pasadas.
-   💬 **Síntesis Humana:** El Director Nexus genera informes empáticos y profesionales integrando todos los datos técnicos.

---

## 🔐 Seguridad y Configuración (.env)
El sistema incluye un archivo `.env` para gestionar claves de API de forma segura. Si deseas usar modelos como **GPT-4** o **Gemini**, simplemente añade tus claves allí.
> **IMPORTANTE:** Nunca compartas el archivo `.env` ni lo subas a repositorios públicos.

## 🛠️ Requisitos Técnicos
-   **Python:** 3.12+
-   **IA:** Ollama (modelo `llama3.2:1b` instalado).
-   **Librerías:** `langgraph`, `langchain`, `flask`, `torch`, `scikit-learn`, `pill`.

## 📁 Estructura de Archivos Críticos
-   `grafo_nexus.py`: Definición de los nodos y lógica de transición del grafo.
-   `base_agente.py`: Clase maestra para la creación de nuevos agentes.
-   `herramientas_nexus.py`: Definición de las herramientas (tools) que usan los agentes.
-   `nuevas_fases.md`: Plan de desarrollo y registro de fases completadas.

---
**Desarrollado con ❤️ para el Ecosistema Nexus - 2026 Roadmap**
