# 🔄 Guía de Adaptación del Sistema IA (AI Factory)

Esta guía sirve como manual para entender cómo crear **cualquier tipo de asistente** (Asesor Legal, Experto Financiero, Programador, Asistente de Ventas, etc.) utilizando la nueva arquitectura del **AI Agent Factory**.

La arquitectura de este proyecto es completamente **dinámica y agnóstica**. Ya no necesitas clonar código ni modificar archivos Python para cambiar el comportamiento del agente; todo se gestiona desde la interfaz gráfica y la base de datos.

---

## 🌟 Estado Actual del Ecosistema

Tu ecosistema ahora es una **Plataforma de Agentes (Factory)**:

*   ✅ **Infraestructura Robusta**: Docker + Postgres (memoria/config) + Qdrant (memoria vectorial) funcionando en segundo plano.
*   ✅ **Interfaz No-Code**: Gestión total de agentes desde el panel web en `http://localhost:3000`.
*   ✅ **Cerebro Dinámico**: El backend (FastAPI + LangGraph) compila el flujo de comportamiento al vuelo según el agente seleccionado.
*   ✅ **Base de Conocimiento (RAG)**: Cada agente puede aprender de documentos propios (PDF, DOCX, TXT) indexados localmente.
*   ✅ **Privacidad Total**: Uso de **Ollama** para LLM (`qwen2.5:7b`) y Embeddings (`nomic-embed-text`), asegurando que tus datos nunca salgan de tu máquina.

---

## 🛠️ Cómo crear un NUEVO Agente (Cualquier Temática)

Si mañana quieres crear un agente de Bioinformática, Abogacía o Marketing, solo sigue estos pasos:

1.  **Desde la Web**: Abre `http://localhost:3000` y pulsa en **+ Crear Nuevo Agente**.
2.  **Configura su "Cerebro"**:
    *   **System Prompt**: Define aquí su personalidad y reglas (ej: "Eres un abogado experto en derecho laboral español...").
    *   **Motor de IA**: Elige "Local: Ollama" para máxima privacidad o "Nube: Google Gemini" para mayor potencia.
    *   **Habilitar RAG**: Actívalo si quieres que el agente consulte documentos.
3.  **¡Listo!**: El agente aparecerá en tu lista y estará listo para chatear.

---

## 📚 Gestión de Documentos (RAG)

Los agentes con RAG activado tienen su propia "memoria de estudio".

### Cómo entrenar a un agente
1.  Haz clic en el botón **📚 Documentos** de tu agente en la lista.
2.  Sube tus archivos (**PDF, DOCX, TXT**).
3.  El sistema dividirá el texto en fragmentos (chunks) y los guardará en una colección de Qdrant exclusiva para ese agente (`agent_{id}`).

### Cómo responde el agente
Cuando haces una pregunta, el sistema:
1.  Busca en su colección de Qdrant los fragmentos más relevantes.
2.  Se los entrega al LLM como "Contexto extraído".
3.  El LLM responde basándose **exclusivamente** (o prioritariamente) en esa información.

---

## 🚀 Uso Avanzado (Desarrolladores)

### Añadir nuevas herramientas (Tools)
Edita `backend/tools/tool_registry.py`. Define tu función con el decorador `@tool` y añádela al diccionario `AVAILABLE_TOOLS`. El sistema la detectará automáticamente.

### Modificar el flujo de pensamiento
Edita `backend/core/agent_factory.py`. Aquí se define el grafo de LangGraph (`StateGraph`). Puedes añadir nodos intermedios para procesos de validación, búsqueda en internet o ejecución de código.

### Comandos útiles de API
```bash
# Chatear por consola
curl -X POST http://localhost:8000/api/v1/agent/2/chat \
     -H "Content-Type: application/json" \
     -d '{"input": "Hola, ¿qué dice el manual sobre las vacaciones?", "session_id": "test"}'

# Subir un documento
curl -X POST http://localhost:8000/api/v1/agent/2/documents -F "file=@manual.pdf"
```

---

## 🔧 Puesta en Marcha Rápida

1.  **Infraestructura**: `docker compose up -d`
2.  **Backend**: `cd backend && source venv/bin/activate && uvicorn main:app --reload`
3.  **Frontend**: `cd frontend && npm start`

*   **Panel Web**: [http://localhost:3000](http://localhost:3000)
*   **Documentación API**: [http://localhost:8000/docs](http://localhost:8000/docs)
