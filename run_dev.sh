#!/bin/bash

# Script para ejecutar el entorno de desarrollo de SIFU

echo "🚀 Iniciando SIFU - Entorno de desarrollo"
echo "=================================================="

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verificar Python
if ! command_exists python3; then
    echo "❌ Error: Python 3 no está instalado"
    exit 1
fi

# Verificar pip
if ! command_exists pip; then
    echo "❌ Error: pip no está instalado"
    exit 1
fi

# Verificar Node.js
if ! command_exists node; then
    echo "❌ Error: Node.js no está instalado"
    echo "   Instalar desde: https://nodejs.org/"
    exit 1
fi

# Verificar npm
if ! command_exists npm; then
    echo "❌ Error: npm no está instalado"
    exit 1
fi

echo "✅ Dependencias del sistema verificadas"

# Instalar dependencias de Python si no existen
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual de Python..."
    python3 -m venv venv
fi

echo "🔄 Activando entorno virtual..."
source venv/bin/activate

echo "📦 Instalando dependencias de Python..."
pip install -r requirements.txt

# Instalar dependencias de Node.js si no existen
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Instalando dependencias de Node.js..."
    cd frontend
    npm install
    cd ..
fi

echo "🎯 Iniciando servidores de desarrollo..."

# Función para limpiar procesos al salir
cleanup() {
    echo ""
    echo "🛑 Deteniendo servidores..."
    kill $(jobs -p) 2>/dev/null
    exit 0
}

# Configurar trap para cleanup
trap cleanup INT TERM

# Iniciar backend en segundo plano
echo "🐍 Iniciando backend FastAPI en puerto 8000..."
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Esperar un momento para que el backend inicie
sleep 3

# Iniciar frontend en segundo plano
echo "⚛️  Iniciando frontend React en puerto 3000..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Servidores iniciados correctamente!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Frontend (React):     http://localhost:3000"
echo "🔗 API Backend:         http://localhost:8000"
echo "📖 Documentación API:   http://localhost:8000/api/docs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Presiona Ctrl+C para detener ambos servidores"
echo ""

# Esperar a que terminen los procesos
wait 