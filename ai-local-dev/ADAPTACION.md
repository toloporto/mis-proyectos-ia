# 🔄 Guía de Adaptación del Sistema IA (AI Factory)

Esta guía te servirá como manual para entender cómo crear **cualquier tipo de asistente** (Asesor Legal, Experto Financiero, Programador, Asistente de Ventas, etc.) utilizando la nueva arquitectura del **AI Agent Factory**.

La arquitectura de este proyecto es completamente **dinámica y agnóstica**. A diferencia de las versiones anteriores donde tenías que clonar código y modificar archivos Python para cambiar el comportamiento del agente, ahora todo se gestiona desde la interfaz gráfica y la base de datos.

---

## 🌟 Estado FINAL del Ecosistema

Tu ecosistema actual es una **Plataforma (Factory)**:

✅ **Docker + Postgres + Qdrant**: Base de datos de memoria (Postgres) y vectorial (Qdrant) funcionando de fondo.
✅ **Creación UI (No-Code)**: Ya no necesitas editar código para crear agentes. Todo se hace desde el panel de administración web.
✅ **Motor Dinámico (FastAPI + LangGraph)**: El backend compila el grafo de comportamiento del agente al vuelo dependiendo del agente con el que estés hablando.
✅ **Herramientas (Tools)**: Soporte integrado para Code Interpreter, búsqueda RAG y herramientas personalizadas.

---

## 🛠️ Cómo crear un NUEVO Agente (Cualquier Temática)

Si mañana quieres hacer un agente de Bioinformática, Abogacía o Marketing, ya no tienes que copiar carpetas ni tocar código. Solo sigue estos pasos:

### 1. Desde la Interfaz Web
Abre `http://localhost:3000` y haz clic en **+ Crear Nuevo Agente**.

### 2. Configura su "Cerebro"
Rellena los campos con la personalidad que necesites:
- **Nombre**: (Ej. Dr. Genoma)
- **Rol**: (Ej. Bioinformático Experto)
- **Motor de IA (LLM)**: Elige "Local: Ollama" para privacidad total y uso gratuito sin límite (evita errores de API Keys), o "Nube: Google Gemini" si cuentas con una clave válida de Google Cloud.
- **System Prompt**: Aquí es donde le das las instrucciones exactas de cómo debe comportarse, qué debe saber y cómo debe responder. (Ej. *"Eres un experto en bioinformática. Tus respuestas deben ser analíticas y utilizar nomenclatura científica..."*).

### 3. ¡Listo para interactuar!
En cuanto le des a "Guardar", el agente aparecerá en tu lista. Al seleccionarlo, el backend cargará su perfil y podrás empezar a chatear. LangGraph y PostgreSQL se encargarán de recordar el historial de esa conversación específica.

---

## 🚀 Uso Avanzado (Para Desarrolladores)

Si necesitas hacer modificaciones profundas al motor interno (por ejemplo, para añadir nuevas herramientas a los agentes), aquí es donde debes tocar:

1. **Añadir nuevas Herramientas (Tools)**:
   Abre `backend/tools/tool_registry.py` y define tus herramientas usando el decorador `@tool` de LangChain. Luego añádelas al diccionario `AVAILABLE_TOOLS`. 

2. **Cambiar el flujo de pensamiento del Agente**:
   Si quieres que el agente pase por un supervisor antes de responder, o que haga bucles de comprobación, edita `backend/core/agent_factory.py`. Ahí es donde se dibuja el grafo (`StateGraph`) que conecta las acciones del agente.

3. **Interactuar mediante la API (Sin Web)**:
   Si quieres conectar un agente a WhatsApp, Telegram o tu propio programa, puedes usar la API directamente:
   ```bash
   curl -X POST http://localhost:8000/api/v1/agent/1/chat \
        -H "Content-Type: application/json" \
        -d '{"input": "Hola, ¿cómo estás?", "session_id": "usuario_telegram_123"}'
   ```
   *(Cambia el `1` por el ID del agente que creaste).*

**¡TU MÁQUINA ESTÁ LISTA PARA IA OPEN SOURCE ILIMITADA! 🚀**
