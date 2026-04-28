# 🏥 Sistema Multiagente Médico con LangGraph y Ollama

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green.svg)](https://langchain-ai.github.io/langgraph/)
[![Ollama](https://img.shields.io/badge/Ollama-0.3+-orange.svg)](https://ollama.ai)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-teal.svg)](https://fastapi.tiangolo.com)
[![SQLite](https://img.shields.io/badge/SQLite-3-blue.svg)](https://sqlite.org)

## 📋 Tabla de Contenidos

- [Descripción General](#descripción-general)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Características Principales](#características-principales)
- [Requisitos Previos](#requisitos-previos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Ejecución del Sistema](#ejecución-del-sistema)
- [API REST](#api-rest)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Modelos de IA Soportados](#modelos-de-ia-soportados)
- [Base de Datos](#base-de-datos)
- [Ejemplos de Uso](#ejemplos-de-uso)
- [Solución de Problemas](#solución-de-problemas)
- [Próximas Mejoras](#próximas-mejoras)
- [Licencia](#licencia)

## Descripción General

El **Sistema Multiagente Médico** es una aplicación de inteligencia artificial que utiliza **LangGraph** para orquestar múltiples agentes IA especializados que trabajan en cadena para proporcionar triage, diagnóstico y tratamiento médico. El sistema es **completamente gratuito y local**, utilizando **Ollama** para ejecutar modelos de lenguaje sin conexión a internet.

### 🤖 ¿Cómo funciona?

Paciente → Síntomas → [Agente 1: TRIAGE] → [Agente 2: DIAGNÓSTICO] → [Agente 3: TRATAMIENTO] → Resultado
↓ ↓ ↓
Clasifica urgencia Identifica condición Recomienda acciones


## Arquitectura del Sistema

┌─────────────────────────────────────────────────────────────────────────────┐
│ INTERFAZ DE USUARIO │
├─────────────────┬─────────────────┬─────────────────┬───────────────────────┤
│ CLI (Python) │ Web (HTML/CSS) │ API REST │ Swagger Docs │
└────────┬────────┴────────┬────────┴────────┬────────┴───────────┬───────────┘
│ │ │ │
▼ ▼ ▼ ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ SISTEMA MULTIAGENTE (LangGraph) │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │ TRIAGE │ → │ DIAGNÓSTICO │ → │ TRATAMIENTO │ → │ EDUCACIÓN │ │
│ │ (Agente 1) │ │ (Agente 2) │ │ (Agente 3) │ │ (Agente 4) │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
│ ↓ │
│ ┌─────────────────────┐ │
│ │ MEMORIA COMPARTIDA │ │
│ └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ CAPA DE IA │
├─────────────────────────────────────────────────────────────────────────────┤
│ 🦙 OLLAMA (Local) │
│ ┌─────────────────────────────────────┐ │
│ │ Modelos: phi3 / llama3.1 / antolin │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ PERSISTENCIA │
├─────────────────────────────────────────────────────────────────────────────┤
│ 🗄️ SQLite Database │
│ ┌─────────────────────────────────────┐ │
│ │ pacientes | consultas | agentes_log │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘


## Características Principales

### 🤖 Sistema Multiagente
- **4 agentes especializados**: Triage, Diagnóstico, Tratamiento y Educación
- **Orquestación con LangGraph**: Control de flujo mediante grafos
- **Memoria compartida**: Cada agente conoce el contexto de los anteriores
- **Procesamiento en cadena**: Flujo automático sin intervención

### 🧠 Modelos de IA Locales
- **Completamente gratuito**: Sin costes de API
- **Sin internet requerida**: Todo corre localmente
- **Múltiples modelos**: phi3 (rápido), llama3.1 (potente), tinyllama (ultra-rápido)
- **Privacidad total**: Los datos nunca salen de tu equipo

### 🌐 Interfaces Disponibles
- **CLI interactiva**: Menú en terminal
- **API REST**: Endpoints para integración
- **Interfaz Web**: UI amigable con CSS moderno
- **Documentación Swagger**: Pruebas interactivas de API

### 💾 Persistencia de Datos
- **SQLite**: Base de datos local
- **Historial de consultas**: Todas las consultas quedarán guardadas
- **Logs de agentes**: Seguimiento individual de cada agente
- **Gestión de pacientes**: Registro y seguimiento

### 🔧 Funcionalidades
- ✅ Validación de síntomas
- ✅ Clasificación de urgencia (LEVE/MODERADO/GRAVE/EMERGENCIA)
- ✅ Diagnóstico diferencial
- ✅ Recomendaciones de tratamiento
- ✅ Consejos para pacientes (lenguaje claro)
- ✅ Estadísticas del sistema
- ✅ Búsqueda de pacientes
- ✅ Exportación de datos

## Requisitos Previos

### Hardware Recomendado
| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| RAM | 8 GB | 16 GB |
| CPU | 2 núcleos | 4+ núcleos |
| Disco | 10 GB libres | 20 GB+ |
| GPU | No requerida | Opcional (mejora velocidad) |

### Software Requerido
- **Windows 11 Pro** con WSL2 habilitado
- **Ubuntu 22.04 o superior** (dentro de WSL)
- **Python 3.12+**
- **Ollama** (para modelos locales)
- **Espacio en disco**: ~5-10 GB para modelos

## Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/langGraph-Telemedicina.git
cd langGraph-Telemedicina

2. Crear y Activar Entorno Virtual

python -m venv venv
source venv/bin/activate  # En WSL/Ubuntu
# o
venv\Scripts\activate     # En Windows

3. Instalar Dependencias

pip install --upgrade pip
pip install langgraph langchain python-dotenv
pip install requests fastapi uvicorn
pip install numpy pandas  # Opcional, para procesamiento de datos

4. Instalar Ollama (si no está instalado)

curl -fsSL https://ollama.ai/install.sh | sh

5. Descargar Modelo de IA

# Modelo recomendado (rápido y buena calidad)
ollama pull phi3:latest

# Alternativas
ollama pull llama3.2:3b    # Balance calidad/velocidad
ollama pull tinyllama:latest  # Ultra rápido (menos calidad)

6. Verificar Instalación

ollama list
# Deberías ver el modelo descargado

python -c "import langgraph; print('LangGraph OK')"


Configuración

Estructura de Directorios

mkdir -p datos src/agents src/tools src/models src/utils src/database
touch src/__init__.py src/agents/__init__.py src/tools/__init__.py

Archivo de Configuración (opcional)

cat > .env << EOF
# Modelo por defecto
DEFAULT_MODEL=phi3:latest
API_PORT=8000
EOF


Ejecución del Sistema

🖥️ Interfaz de Línea de Comandos (CLI)

# Sistema original (validación manual)
python src/main.py

# Sistema multiagente profesional
python src/agents/sistema_multiagente_profesional_rapido.py

# Sistema con base de datos
python src/agents/sistema_phi3_db.py

🌐 API REST

# Iniciar servidor API
python src/api/api.py

# El servidor se ejecutará en http://localhost:8000

🎨 Interfaz Web

# Asegúrate que la API esté corriendo
# Abre en tu navegador:
# http://localhost:8000/web

API REST
Endpoints Disponibles
Método	Endpoint	                Descripción	                Ejemplo
GET	        /	                    Información de la API	        -
GET	    /health	                    Estado del sistema	            -
POST	/consultar	                Realizar consulta médica	{"sintomas": "dolor cabeza", "edad": 30}
GET	    /estadisticas	            Estadísticas del sistema	    -
GET	    /consultas	                Listar consultas	        ?limite=10
GET	    /pacientes	                Listar pacientes	            -
GET	    /consultas/paciente/{id}	Consultas por paciente	    /consultas/paciente/1
DELETE	/consultas/{id}	            Eliminar consulta	        /consultas/5
GET	    /web	                    Interfaz web	                -
GET	    /docs	                    Documentación Swagger	        -


Ejemplo de Uso con cURL

# Consulta médica
curl -X POST http://localhost:8000/consultar \
  -H "Content-Type: application/json" \
  -d '{
    "sintomas": "dolor de cabeza y fiebre",
    "nombre_paciente": "Juan Perez",
    "edad": 35
  }'

# Ver estadísticas
curl http://localhost:8000/estadisticas

# Ver últimas consultas
curl http://localhost:8000/consultas?limite=5

Ejemplo de Respuesta

{
  "id": 1,
  "sintomas": "dolor de cabeza y fiebre",
  "triage": "MODERADO - Requiere atención en 24h",
  "diagnostico": "Posible infección viral aguda",
  "tratamiento": "Reposo, hidratación y paracetamol si es necesario",
  "nivel_urgencia": "MODERADO",
  "tiempo_procesamiento": 35.2,
  "timestamp": "2024-01-15T10:30:00"
}



Estructura del Proyecto

langGraph-Telemedicina/
│
├── datos/                          # Datos persistentes
│   ├── pacientes.json              # Pacientes registrados
│   ├── consultas.db                # Base de datos SQLite
│   └── consultas_profesionales.json # Historial de consultas
│
├── src/
│   ├── main.py                     # Aplicación CLI principal
│   │
│   ├── agents/                     # Agentes IA
│   │   ├── sistema_multiagente_medico.py
│   │   ├── sistema_multiagente_profesional_rapido.py
│   │   ├── sistema_phi3_db.py     # Con integración BD
│   │   └── sistema_tinyllama.py    # Versión ultra rápida
│   │
│   ├── api/                        # API REST
│   │   └── api.py                  # FastAPI endpoints
│   │
│   ├── database/                   # Capa de persistencia
│   │   └── database.py             # SQLite ORM simple
│   │
│   ├── tools/                      # Herramientas auxiliares
│   │   ├── validador_sintomas.py   # Validación local
│   │   └── buscador.py             # Búsqueda de pacientes
│   │
│   ├── models/                     # Modelos de datos
│   │   └── paciente.py             # Clase Paciente
│   │
│   └── utils/                      # Utilidades
│       ├── config.py               # Configuración
│       └── persistencia.py         # Persistencia JSON
│
├── venv/                           # Entorno virtual
├── .env                            # Variables de entorno
└── README.md                       # Este archivo




Modelos de IA Soportados

Comparativa de Modelos
Modelo	            Tamaño	            Velocidad	        Calidad	                Uso recomendado
phi3:latest	        2.2 GB	            ⚡⚡⚡	            ⭐⭐⭐⭐	            Recomendado
llama3.2:3b	        2.0 GB	            ⚡⚡⚡	            ⭐⭐⭐⭐	            Pruebas generales
tinyllama:latest	637 MB	            ⚡⚡⚡⚡	       ⭐⭐	                  Respuestas rápidas
llama3.1:latest	    4.9 GB	            ⚡⚡	              ⭐⭐⭐⭐⭐	            Calidad máxima
antolin-dev	        4.7 GB	            ⚡⚡	              ⭐⭐⭐⭐	              Modelo personalizado


Cambiar Modelo

# En cualquier archivo de agente
MODELO = "phi3:latest"  # Cambiar según necesidad

Base de Datos

Esquema SQLite

-- Tabla de pacientes
CREATE TABLE pacientes (
    id INTEGER PRIMARY KEY,
    nombre TEXT,
    edad INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de consultas
CREATE TABLE consultas (
    id INTEGER PRIMARY KEY,
    paciente_id INTEGER,
    sintomas TEXT,
    triage TEXT,
    diagnostico TEXT,
    tratamiento TEXT,
    nivel_urgencia TEXT,
    tiempo_procesamiento REAL,
    modelo_ia TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
);

-- Tabla de logs de agentes
CREATE TABLE agentes_log (
    id INTEGER PRIMARY KEY,
    consulta_id INTEGER,
    agente_nombre TEXT,
    agente_respuesta TEXT,
    tiempo_ejecucion REAL,
    orden INTEGER,
    FOREIGN KEY (consulta_id) REFERENCES consultas(id)
);

Consultar Datos Directamente

sqlite3 datos/consultas.db
> SELECT * FROM consultas ORDER BY created_at DESC LIMIT 5;
> .exit

Ejemplos de Uso
Ejemplo 1: Consulta de Síntomas Leves
python src/agents/sistema_phi3_db.py
# Síntomas: "Dolor de cabeza leve y algo de cansancio"

# Respuesta esperada:
# 🔴 TRIAGE: LEVE - Seguimiento en domicilio
# 🩺 DIAGNÓSTICO: Posible estrés o falta de sueño
# 💊 TRATAMIENTO: Reposo e hidratación

Ejemplo 2: Consulta de Urgencia


# Síntomas: "Dificultad para respirar y dolor en el pecho"

# Respuesta esperada:
# 🔴 TRIAGE: EMERGENCIA - Requiere atención inmediata
# 🩺 DIAGNÓSTICO: Posible problema cardíaco o respiratorio
# 💊 TRATAMIENTO: ACUDA A URGENCIAS INMEDIATAMENTE

Ejemplo 3: Uso de la API

import requests

response = requests.post(
    "http://localhost:8000/consultar",
    json={"sintomas": "Dolor de estómago y náuseas", "edad": 25}
)
print(response.json())

Solución de Problemas

Error: "Ollama no está corriendo"
# En una terminal separada
ollama serve

# Verificar que funciona
ollama list

Error: "ModuleNotFoundError"

# Activar entorno virtual e instalar dependencias
source venv/bin/activate
pip install -r requirements.txt  # o instalar manualmente

Error: "Timeout en consulta"

# Aumentar timeout en el archivo correspondiente
# Buscar "timeout=" y cambiar a 45 o 60 segundos

Error: "Puerto 8000 ya está en uso"

# Cambiar puerto en api.py
uvicorn.run(app, host="0.0.0.0", port=8001)

# O matar el proceso que usa el puerto
lsof -i :8000
kill -9 <PID>

Respuestas Incoherentes

# Probar con otro modelo
ollama pull phi3:latest  # Cambiar en el código a phi3

Próximas Mejoras

Interfaz móvil: App para Android/iOS

Más agentes: Especialidades médicas (Cardiología, Neurología)

Integración con Telegram/WhatsApp: Bot para consultas

Exportar informes en PDF: Resultados formateados

Dashboard de administración: Gráficos y métricas

Soporte para múltiples idiomas: Inglés, portugués

Reconocimiento de voz: Entrada por voz

Sistema de alertas: Notificaciones para seguimiento

Licencia
MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files...


🙏 Agradecimientos

LangGraph - Framework para agentes

Ollama - Modelos locales

FastAPI - Framework API

Microsoft - WSL2


📞 Contacto y Soporte

Issues: GitHub Issues

Email: tu-email@ejemplo.com

⭐ ¡Si te gusta este proyecto, no olvides darle una estrella en GitHub!


Este README proporciona una documentación completa y profesional para tu aplicación. ¿Quieres que añada o modifique alguna sección específica? 🚀
