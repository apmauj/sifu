#!/bin/bash

# Script para ejecutar solo el BACKEND de SIFU
# Sistema de Índices Financieros del Uruguay

echo "🚀 Iniciando SIFU Backend"
echo "========================="

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

echo "✅ Dependencias de Python verificadas"

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual de Python..."
    python3 -m venv venv
fi

echo "🔄 Activando entorno virtual..."
source venv/bin/activate

echo "📦 Instalando/actualizando dependencias..."
pip install -r requirements.txt

# Función para cleanup al salir
cleanup() {
    echo ""
    echo "🛑 Deteniendo servidor backend..."
    exit 0
}

# Configurar trap para cleanup
trap cleanup INT TERM

echo ""
echo "🚀 Iniciando FastAPI Backend..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔗 API Backend:         http://localhost:8000"
echo "📖 Documentación API:   http://localhost:8000/api/docs" 
echo "🔧 API Redoc:           http://localhost:8000/redoc"
echo "📊 Health Check:        http://localhost:8000/api/health"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 Tip: Para probar la API desde terminal:"
echo "   curl http://localhost:8000/api/health"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo ""

# Iniciar backend con hot reload
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 