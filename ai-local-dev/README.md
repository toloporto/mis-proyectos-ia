# 🤖 AI Agent Factory

Bienvenido al ecosistema local y universal de Inteligencia Artificial. Este proyecto ha evolucionado de un asistente de ortodoncia estático a una **Plataforma Multi-Agente Dinámica**. Ahora puedes crear y gestionar cualquier tipo de agente desde la propia interfaz web, almacenando sus configuraciones en base de datos y manteniendo un historial persistente automáticamente.

## 🏗️ Nueva Arquitectura del Ecosistema

El proyecto está compuesto por los siguientes pilares:

1. **Frontend Dinámico (React)**: Interfaz dividida en un Panel de Control (Sidebar) para crear/seleccionar agentes, y un entorno de Chat enriquecido.
2. **Backend Engine (FastAPI + LangGraph)**: Servidor Python que ensambla los grafos de LangGraph de manera dinámica basándose en la configuración del agente (LLM, RAG, Herramientas).
3. **Persistencia (PostgreSQL)**: Base de datos relacional corriendo en Docker (Puerto `5432`). Guarda las configuraciones de los agentes y la memoria (Checkpointer) de cada conversación.
4. **Base Vectorial (Qdrant)**: Base de datos vectorial corriendo en Docker (Puertos `6333`, `6334`). Preparada para Retrieval-Augmented Generation (RAG) dinámico e ingesta de documentos.

---

## 🚀 Guía de Inicio Rápido

Para facilitar el inicio, hemos creado un script que levanta todo el ecosistema (Docker, Backend y Frontend) con un solo comando.

1. Abre tu terminal en la raíz del proyecto.
2. Ejecuta el entorno:
   ```bash
   ./start_factory.sh
   ```

*(El script encenderá las bases de datos en Docker, instalará las dependencias de Python requeridas en el entorno activo y levantará React y FastAPI en segundo plano).*

---

## 🧠 ¿Cómo crear un Agente Nuevo?

1. Entra en `http://localhost:3000`.
2. Haz clic en **"+ Crear Nuevo Agente"** en la barra lateral izquierda.
3. Rellena los datos:
   - **Nombre**: Ej. *Experto Python*
   - **Rol**: Ej. *Senior Developer*
   - **Motor de IA (LLM)**: Elige entre opciones Locales (Ollama) o en la Nube (Google Gemini).
   - **System Prompt**: Ej. *Eres un experto en Python. Responde siempre con código limpio y bien comentado...*
4. Guarda y selecciona el agente en la barra lateral.
5. ¡Empieza a chatear! El backend creará dinámicamente el agente usando LangGraph y persistirá tu conversación en PostgreSQL.

---

## ⚙️ Motores de Inteligencia Artificial (LLMs) y Solución de Errores

El Factory soporta múltiples "motores" o cerebros para tus agentes. Puedes elegir cuál usar al crear un agente en la web:

### 1. Ollama (Local y 100% Privado) - *Recomendado por defecto*
- **Cómo funciona**: Usa la aplicación Ollama instalada en tu ordenador (conecta en `localhost:11434`).
- **Ventajas**: No necesita API Keys, no tiene límite de uso, es 100% gratuito y privado. Nunca fallará por "credenciales inválidas".
- **Requisito**: Debes tener el modelo descargado. Para el que viene por defecto, abre una terminal y ejecuta: `ollama pull llama3.2:1b`.

### 2. Google Gemini (Nube)
- **Cómo funciona**: Se conecta a los servidores de Google usando LangChain.
- **Ventajas**: Modelos extremadamente potentes y rápidos (ej. `gemini-1.5-flash` o `gemini-1.5-pro`).
- **Solución a errores de API**: Si la consola muestra `API key not valid`, significa que la clave ha caducado o ha sido revocada por Google. 
  - **Cómo arreglarlo**: Entra en [Google AI Studio](https://aistudio.google.com/app/apikey), genera una nueva clave gratuita, y actualízala en el archivo `backend/core/agent_factory.py` (en la variable `api_key = os.getenv(...)`).

### Alternativas Futuras
El ecosistema está preparado para añadir **Anthropic (Claude)** o **OpenAI (ChatGPT)**. Solo habría que añadir la opción en el `<select>` de `frontend/src/App.tsx` y su importación respectiva en `backend/core/agent_factory.py`.

---

## 🐳 Guía Definitiva de Comandos Docker y Bases de Datos

Dado que el historial (Postgres) y el conocimiento de los agentes (Qdrant) viven en contenedores Docker, aquí tienes la lista esencial de comandos:

| Comando | ¿Para qué sirve exactamente? |
|---------|-----------------------------|
| `docker compose up -d` | **Levanta TODO en segundo plano (detached).** Enciende los contenedores de Postgres y Qdrant. |
| `docker compose ps` | **Comprobar Estado.** Te muestra una lista de los contenedores y puertos. |
| `docker compose logs postgres` | **Ver Registros (Logs).** Imprime los mensajes internos de Postgres. *(Puedes cambiar `postgres` por `qdrant`).* |
| `docker compose down` | **Para TODO.** Detiene y destruye los contenedores. Tus datos NO se borran porque usan volúmenes persistentes. |
| `docker system prune -f` | **Limpia el disco.** Borra contenedores que ya están detenidos y redes sin uso. |

---

## 🛑 ¿Cómo salir y detener la aplicación?

1. En la terminal donde corriste el script, pulsa `Ctrl + C` repetidas veces para cerrar el Frontend (React) y Backend (FastAPI).
2. Para apagar las bases de datos de Docker, ejecuta: `docker compose down`.
3. Cierra la aplicación de Ollama desde tu barra de tareas de Windows/Mac.
