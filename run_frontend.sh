#!/bin/bash

# Script para ejecutar solo el FRONTEND de SIFU
# Sistema de Índices Financieros del Uruguay

echo "⚛️  Iniciando SIFU Frontend"
echo "==========================="

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

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

echo "✅ Dependencias de Node.js verificadas"

# Verificar si existe el directorio frontend
if [ ! -d "frontend" ]; then
    echo "❌ Error: No se encuentra el directorio 'frontend'"
    echo "   Asegúrate de estar en la raíz del proyecto SIFU"
    exit 1
fi

cd frontend

# Instalar dependencias si no existen
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias de Node.js..."
    npm install
else
    echo "📦 Verificando dependencias..."
    npm install
fi

# Función para cleanup al salir
cleanup() {
    echo ""
    echo "🛑 Deteniendo servidor frontend..."
    exit 0
}

# Configurar trap para cleanup
trap cleanup INT TERM

echo ""
echo "🚀 Iniciando React Development Server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Frontend (React):     http://localhost:3000"
echo "🔧 Hot Reload:           Activado"
echo "📱 Mobile Testing:       http://[tu-ip]:3000"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  IMPORTANTE: Para funcionalidad completa, asegúrate de que el backend esté corriendo:"
echo "   ./run_backend.sh (en otra terminal)"
echo ""
echo "💡 Tip: El frontend se conecta al backend en http://localhost:8000"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo ""

# Iniciar frontend con Vite dev server
npm run dev 