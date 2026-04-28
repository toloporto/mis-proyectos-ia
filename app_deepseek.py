import streamlit as st
from openai import OpenAI
import requests
import os
import subprocess
import sys
import re
import json

# 1. Configuración de la página
st.set_page_config(page_title="DeepSeek Engineer: Senior Suite", page_icon="🚀", layout="wide")

# Estilos de la Consola y UI
st.markdown("""
    <style>
    .console { 
        background-color: #000000; color: #00FF00; font-family: 'Courier New', monospace; 
        padding: 15px; border-radius: 5px; border: 1px solid #4b4b4b; 
        min-height: 150px; white-space: pre-wrap;
    }
    .stCodeBlock { border: 1px solid #4b4b4b; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 DeepSeek Engineer: Senior Suite")

# 2. Cliente Ollama
client = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')

# 3. FUNCIONES DE MEMORIA (Persistencia)
MEMORY_FILE = "proyecto_config.json"

def cargar_memoria():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {"notas": ""}

def guardar_memoria(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# 4. BARRA LATERAL
with st.sidebar:
    st.header("⚙️ Panel de Control")
    modo = st.radio("Herramienta", ["💬 Chat", "🔨 Refactor/Ejecutar", "🧪 Testing & QA", "📐 Arquitecto", "📦 Librerías"])
    
    # Detección de modelos
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=2)
        modelos_instalados = [m['name'] for m in resp.json()['models']]
    except:
        modelos_instalados = ["qwen2.5-coder:7b", "deepseek-coder-v2"]
    
    modelo_seleccionado = st.selectbox("IA Engine", modelos_instalados)
    temperatura = st.slider("Creatividad", 0.0, 1.0, 0.2 if modo != "💬 Chat" else 0.7)
    
    st.divider()

    # Memoria de Proyecto
    st.header("🧠 Memoria del Proyecto")
    memoria = cargar_memoria()
    nueva_nota = st.text_area("Objetivos y notas:", memoria["notas"], height=100)
    if nueva_nota != memoria["notas"]:
        memoria["notas"] = nueva_nota
        guardar_memoria(memoria)
        st.success("Memoria guardada")

    st.divider()

    # Explorador de Archivos
    st.header("📂 Proyecto")
    ruta_actual = os.getcwd()
    archivos_locales = [f for f in os.listdir(ruta_actual) if f.endswith(('.py', '.js', '.html', '.css', '.json', '.txt'))]
    
    archivos_seleccionados = []
    for archivo in archivos_locales:
        if st.checkbox(archivo, key=f"check_{archivo}"):
            archivos_seleccionados.append(archivo)

# 5. LÓGICA DE TRABAJO
if "last_output" not in st.session_state: st.session_state.last_output = ""
if "messages" not in st.session_state: st.session_state.messages = []

# --- MODO LIBRERÍAS ---
if modo == "📦 Librerías":
    st.subheader("📦 Gestión de Librerías Pip")
    st.caption(f"Entorno: `{sys.executable}`")
    col1, col2 = st.columns([2,1])
    with col1:
        nueva_lib = st.text_input("Librería a instalar:", placeholder="ej. pandas matplotlib")
        if st.button("🚀 Instalar"):
            with st.spinner("Instalando..."):
                proc = subprocess.run([sys.executable, "-m", "pip", "install", nueva_lib], capture_output=True, text=True)
                st.session_state.last_output = proc.stdout if proc.returncode == 0 else proc.stderr
    with col2:
        if st.button("📋 Listar instaladas"):
            proc = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True)
            st.session_state.last_output = proc.stdout
    st.markdown(f'<div class="console">{st.session_state.last_output}</div>', unsafe_allow_html=True)

# --- MODO TESTING & QA ---
elif modo == "🧪 Testing & QA":
    st.subheader("🧪 Testing & QA (Pytest)")
    if archivos_seleccionados:
        archivo_testear = st.selectbox("Selecciona archivo para analizar:", archivos_seleccionados)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🪄 Generar código de Test"):
                st.session_state.gen_test = True
                st.session_state.archivo_objetivo = archivo_testear
        with col2:
            if st.button("🚀 Ejecutar Pytest"):
                with st.spinner("Corriendo tests..."):
                    res = subprocess.run([sys.executable, "-m", "pytest", "-v"], capture_output=True, text=True)
                    st.session_state.last_output = res.stdout + "\n" + res.stderr
        st.markdown(f'<div class="console">{st.session_state.last_output}</div>', unsafe_allow_html=True)
    else:
        st.warning("Selecciona archivos en la barra lateral.")

# --- MODO ARQUITECTO ---
elif modo == "📐 Arquitecto":
    st.subheader("📐 Arquitecto: Mapa de Dependencias")
    for arc in archivos_locales:
        with st.expander(f"📄 {arc}"):
            with open(arc, "r", encoding="utf-8") as f:
                imports = re.findall(r"^(?:from|import)\s+([\w\.]+)", f.read(), re.MULTILINE)
                st.write("**Imports:**", list(set(imports)) if imports else "Sin dependencias locales.")

# --- MODO REFACTOR/EJECUTAR ---
elif modo == "🔨 Refactor/Ejecutar":
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📝 Editor")
        if archivos_seleccionados:
            archivo_a_ver = st.selectbox("Viendo:", archivos_seleccionados)
            with open(archivo_a_ver, "r", encoding="utf-8") as f:
                st.code(f.read(), line_numbers=True)
            if st.button("▶️ Ejecutar"):
                try:
                    res = subprocess.run([sys.executable, archivo_a_ver], capture_output=True, text=True, timeout=15)
                    st.session_state.last_output = res.stdout if res.stdout else res.stderr
                except Exception as e: st.session_state.last_output = f"Error: {e}"
    with col2:
        st.subheader("🖥️ Consola")
        st.markdown(f'<div class="console">{st.session_state.last_output}</div>', unsafe_allow_html=True)

# 6. MOTOR DE IA (Chat y Generación)
# Inyectar historial en el chat
if modo == "💬 Chat" or st.session_state.get("gen_test"):
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    # Determinar el prompt
    enviar = False
    if st.session_state.get("gen_test"):
        prompt = f"Genera un archivo de test completo con pytest para el archivo {st.session_state.archivo_objetivo}. Devuelve SOLO el código."
        st.session_state.gen_test = False
        enviar = True
    elif prompt := st.chat_input("¿En qué puedo ayudarte con el proyecto?"):
        enviar = True

    if enviar:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        # Construir contexto
        contexto = f"MEMORIA: {memoria['notas']}\n"
        for arc in archivos_seleccionados:
            with open(arc, "r", encoding="utf-8") as f:
                contexto += f"\nFILE {arc}:\n{f.read()}\n"

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_resp = ""
            stream = client.chat.completions.create(
                model=modelo_seleccionado,
                messages=[{"role": "user", "content": f"{contexto}\n\n{prompt}"}],
                stream=True,
                temperature=temperatura
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_resp += chunk.choices[0].delta.content
                    placeholder.markdown(full_resp + "▌")
            placeholder.markdown(full_resp)
            st.session_state.messages.append({"role": "assistant", "content": full_resp})

            # Lógica de guardado de archivos (Especial para Tests)
            if "```" in full_resp:
                try:
                    code_block = full_resp.split("```")[1].split("\n", 1)[1]
                    sufijo = "test_" if "test" in prompt.lower() else "fix_"
                    nombre_sugerido = f"{sufijo}{archivos_seleccionados[0] if archivos_seleccionados else 'code.py'}"
                    
                    col_s1, col_s2 = st.columns(2)
                    with col_s1:
                        st.download_button("📥 Descargar código", code_block, file_name=nombre_sugerido)
                    with col_s2:
                        if st.button(f"💾 Guardar como {nombre_sugerido}"):
                            with open(nombre_sugerido, "w", encoding="utf-8") as f:
                                f.write(code_block)
                            st.success(f"Archivo {nombre_sugerido} creado en el disco.")
                            st.rerun()
                except: pass