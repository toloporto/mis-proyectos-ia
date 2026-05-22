# DeepSeek Engineer: Senior Suite 🚀

Una completa suite de herramientas para desarrolladores de Inteligencia Artificial que integra modelos locales a través de Ollama. Permite la exploración de código, generación de pruebas unitarias (Testing & QA), ejecución y refactorización, todo desde una única interfaz gráfica interactiva potenciada por Streamlit.

## Características Principales

- **💬 Chat Integrado**: Chatea con tus modelos locales (ej. `qwen2.5-coder`, `deepseek-coder-v2`) con el contexto completo de tus archivos seleccionados.
- **🔨 Refactor/Ejecutar**: Visualiza el código fuente de tus scripts y ejecútalos directamente, visualizando la salida en una terminal web emulada.
- **🧪 Testing & QA**: Genera pruebas automáticas para tus scripts en Python utilizando `pytest`, e incluso permite ejecutarlas con un clic.
- **📐 Arquitecto**: Escanea tu proyecto y construye un mapa de dependencias para entender rápidamente qué librerías requiere cada script.
- **📦 Gestión de Librerías Pip**: Permite instalar nuevas librerías en tu entorno local y listar las dependencias actuales sin necesidad de usar comandos.

## Requisitos Previos

- Python 3.10 o superior.
- [Ollama](https://ollama.com/) instalado y corriendo en tu máquina (puerto local `11434`).
- Modelos recomendados instalados en Ollama (ej. `ollama run qwen2.5-coder:7b`).

## Instalación y Configuración (Windows)

1. **Crear el Entorno Virtual (venv)**:
   ```powershell
   python -m venv venv
   ```

2. **Activar el Entorno Virtual**:
   ```powershell
   .\venv\Scripts\activate
   ```

3. **Instalar Dependencias**:
   ```powershell
   pip install -r requirements.txt
   ```

## Uso de la Suite

Una vez el entorno esté configurado y activo, inicia la aplicación gráfica con Streamlit:

```powershell
streamlit run app_deepseek.py
```

Esto abrirá automáticamente una ventana en tu navegador web por defecto apuntando a `http://localhost:8501`.

## Scripts Incluidos (Ejemplos de Pruebas)

El proyecto viene con varios scripts de ejemplo que puedes usar para probar la suite:

- `calculo.py`: Un simple programa matemático que maneja excepciones.
- `gestion_notas.py`: Ejemplo de escritura segura de archivos.
- `login.py`: Autenticación simulada utilizando `hashlib`.
- `generador.py`: Automatización para crear estructuras de nuevos proyectos.
- `prueba.py` y su prueba asociada `test_prueba.py` para verificar la funcionalidad del módulo Testing & QA.

---
*Desarrollado y optimizado para entornos locales aislados.*
