# 🏥 Sistema Multiagente Médico con LangGraph y Ollama

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green.svg)](https://langchain-ai.github.io/langgraph/)
[![Ollama](https://img.shields.io/badge/Ollama-0.3+-orange.svg)](https://ollama.ai)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-teal.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Descripción

Sistema multiagente médico que utiliza **LangGraph** para orquestar agentes IA especializados en:
- **Triage**: Clasificación de urgencia
- **Diagnóstico**: Identificación de condiciones
- **Tratamiento**: Recomendaciones médicas
- **Educación**: Lenguaje claro para pacientes

**Completamente gratuito y local** usando Ollama. Sin costes de API, sin internet requerida.

## 🏗️ Arquitectura


## ✨ Características

- 🤖 **4 Agentes IA** en cadena con LangGraph
- 🧠 **Modelos locales** con Ollama (phi3, llama3, tinyllama)
- 🌐 **API REST** con FastAPI
- 🎨 **Interfaz web** moderna
- 💾 **Persistencia** SQLite
- 📊 **Estadísticas** del sistema
- 🔍 **Búsqueda** de pacientes

## 📦 Requisitos

- Windows 11 Pro con WSL2 o Linux
- Python 3.12+
- Ollama instalado
- 8GB RAM mínimo (16GB recomendado)

## 🚀 Instalación Rápida

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/langGraph-Telemedicina.git
cd langGraph-Telemedicina

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Instalar modelo de IA
ollama pull phi3:latest

# 5. Ejecutar
python src/main.py

🎯 Uso

CLI Interactiva
python src/main.py

API REST
python src/api/api.py
# Abrir http://localhost:8000/web

API REST
bash
python src/api/api.py
# Abrir http://localhost:8000/web
Consultar API
bash
curl -X POST http://localhost:8000/consultar \
  -H "Content-Type: application/json" \
  -d '{"sintomas": "dolor de cabeza", "edad": 30}'
📁 Estructura
text
langGraph-Telemedicina/
├── src/
│   ├── agents/          # Agentes IA
│   ├── api/             # API REST
│   ├── database/        # Persistencia
│   ├── tools/           # Utilidades
│   └── models/          # Modelos de datos
├── datos/               # Base de datos
├── requirements.txt
└── README.md
🔧 Modelos Soportados
Modelo	Tamaño	Velocidad	Calidad	Recomendación
phi3	2.2GB	⚡⚡⚡	⭐⭐⭐⭐	✅ Recomendado
llama3.2:3b	2GB	⚡⚡⚡	⭐⭐⭐⭐	Buen balance
tinyllama	637MB	⚡⚡⚡⚡	⭐⭐	Ultra rápido
📝 Ejemplo
Entrada: "Dolor de cabeza, mareos y náuseas"

Salida:

text
🔴 TRIAGE: MODERADO - Evaluación en 24h
🩺 DIAGNÓSTICO: Posible migraña o infección viral
💊 TRATAMIENTO: Reposo, hidratación, evitar luces brillantes
🤝 Contribuciones
Las contribuciones son bienvenidas. Por favor:

Fork el proyecto

Crea tu branch (git checkout -b feature/AmazingFeature)

Commit tus cambios

Push al branch

Abre un Pull Request

📄 Licencia
MIT License - ver LICENSE para detalles

🙏 Agradecimientos
LangGraph

Ollama

FastAPI

⭐ ¡No olvides darle una estrella si te es útil!

text

### 1.4 Crear archivo `LICENSE`

```bash
nano LICENSE
Copia este contenido (MIT License):

txt
MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
1.5 Crear archivo de ejemplo .env.example
bash
nano .env.example
env
# Modelo por defecto para Ollama
DEFAULT_MODEL=phi3:latest

# Configuración de API
API_HOST=0.0.0.0
API_PORT=8000

# OpenAI (opcional - solo si se usa)
# OPENAI_API_KEY=tu_clave_aqui
1.6 Crear script de inicio rápido
bash
nano setup.sh
chmod +x setup.sh
bash
#!/bin/bash
# Script de instalación automática

echo "🚀 Instalando Sistema Multiagente Médico..."
echo "============================================="

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado"
    exit 1
fi

# Crear entorno virtual
echo "📦 Creando entorno virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

# Verificar Ollama
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama no está instalado"
    echo "   Instálalo con: curl -fsSL https://ollama.ai/install.sh | sh"
else
    echo "🦙 Descargando modelo phi3 (2.2GB)..."
    ollama pull phi3:latest
fi

echo ""
echo "✅ Instalación completada!"
echo ""
echo "Para ejecutar:"
echo "  python src/main.py      # CLI"
echo "  python src/api/api.py   # API"
echo ""
