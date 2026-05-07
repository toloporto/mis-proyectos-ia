#!/bin/bash
echo "Iniciando AI Agent Factory..."

# Levantar DBs
docker compose up -d

# Levantar Backend
cd backend
echo "Instalando dependencias..."
pip install -r requirements-factory.txt
echo "Levantando FastAPI..."
uvicorn main:app --reload --port 8000 &

# Levantar Frontend
cd ../frontend
echo "Instalando módulos de Node..."
npm install
echo "Levantando React..."
npm start
