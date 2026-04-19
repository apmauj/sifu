# 📚 Documentación SIFU

Bienvenido al centro de documentación del proyecto **SIFU - Sistema de Índices Financieros del Uruguay**. Aquí encontrarás toda la información técnica y de desarrollo necesaria.

## 📋 Índice de Documentación

### 🏠 **Documentación Principal**
- [📖 README Principal](../README.md) - Introducción y guía de inicio
- [🏗️ Arquitectura Técnica](./ARCHITECTURE.md) - Diseño completo del sistema
- [📊 Resumen Técnico](./TECHNICAL_SUMMARY.md) - Visión general del proyecto
- [🐍 Plan Upgrade Python](./PYTHON_UPGRADE_ARCHITECTURE_PLAN.md) - Diagnóstico y plan por fases para evolución de runtime

### 🔧 **Documentación de Desarrollo**
- [📡 API Reference](./API_REFERENCE.md) - Documentación completa de endpoints
- [🌐 Guía Frontend](./FRONTEND_GUIDE.md) - Desarrollo del frontend React
- [🧪 Setup de Testing](../README.md#-testing) - Comandos de ejecución de pruebas
- [🚀 Deploy Backend](./DEPLOY_BACKEND.md) - Guía de despliegue del backend
- [🐍 Upgrade Local Seguro](./PYTHON_LOCAL_SAFE_UPGRADE.md) - Migración de entorno local en paralelo (3.11/3.12)
- [📏 Medición Python 3.12](./PYTHON_312_MEASUREMENT_PLAN.md) - Métricas para evaluar impacto (performance/seguridad/estabilidad)

### 📊 **Análisis Técnico**
- [⚙️ Arquitectura de Componentes](./ARCHITECTURE.md#componentes-principales) - Detalles de cada capa
- [🔄 Flujo de Datos](./ARCHITECTURE.md#flujo-de-datos-completo) - Pipeline completo
- [🎯 Patrones de Diseño](./ARCHITECTURE.md#patrones-de-diseño-aplicados) - Patrones implementados
- [📈 Métricas de Performance](./TECHNICAL_SUMMARY.md#métricas-de-performance) - Rendimiento del sistema

---

## 🎯 Documentación por Audiencia

### 👨‍💻 **Para Desarrolladores**
1. **Empezar aquí**: [README Principal](../README.md)
2. **Entender la arquitectura**: [Arquitectura Técnica](./ARCHITECTURE.md)
3. **Trabajar con la API**: [API Reference](./API_REFERENCE.md)
4. **Desarrollar frontend**: [Guía Frontend](./FRONTEND_GUIDE.md)

### 🏗️ **Para Arquitectos**
1. **Diseño del sistema**: [Arquitectura Técnica](./ARCHITECTURE.md)
2. **Análisis técnico**: [Resumen Técnico](./TECHNICAL_SUMMARY.md)
3. **Patrones aplicados**: [Patrones de Diseño](./ARCHITECTURE.md#patrones-de-diseño-aplicados)
4. **Escalabilidad**: [Roadmap Node 24 Actions](./ROADMAP_NODE24_ACTIONS.md)

### 🚀 **Para DevOps**
1. **Instalación**: [README Principal](../README.md#-instalación-y-uso)
2. **Docker**: [Instalación con Docker](../README.md#-instalación-con-docker)
3. **Despliegue**: [Deploy Backend](./DEPLOY_BACKEND.md)
4. **Monitoreo**: [Performance Metrics](./TECHNICAL_SUMMARY.md#métricas-de-performance)

### 📊 **Para Analistas**
1. **Fuentes de datos**: [Data Sources](./ARCHITECTURE.md#data-sources)
2. **Estadísticas**: [Estadísticas de Datos](./TECHNICAL_SUMMARY.md#estadísticas-de-datos)
3. **API endpoints**: [API Reference](./API_REFERENCE.md)
4. **Análisis de datos**: [Capacidades del Sistema](./TECHNICAL_SUMMARY.md#capacidades-implementadas)

---

## 📖 Guías Rápidas

### 🚀 **Quick Start**
```bash
# 1. Clonar el proyecto
git clone <repository>
cd sifu

# 2. Ejecutar con Docker
chmod +x docker-scripts.sh
./docker-scripts.sh up

# 3. Acceder
# Frontend: http://localhost
# API: http://localhost:8000
# Docs: http://localhost:8000/api/docs
```

### 🔧 **Desarrollo Local**
```bash
# Backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --reload

# Frontend (cuando esté disponible)
cd frontend
npm install
npm run dev
```

### 📡 **Usar la API**
```bash
# Obtener último valor UI
curl http://localhost:8000/api/ui/latest

# Obtener cotizaciones
curl http://localhost:8000/api/exchange-rate/latest

# Documentación interactiva
open http://localhost:8000/api/docs
```

---

## 🏗️ Arquitectura en Resumen

```
📊 Data Sources (INE, BHU, BCU)
         ↓
🔄 Processing Layer (Processors)
         ↓
💾 Database Layer (SQLite)
         ↓
⚙️ Service Layer (Business Logic)
         ↓
📡 API Layer (FastAPI - 23 endpoints)
         ↓
🌐 Frontend Layer (React)
```

## 📊 Módulos del Sistema

### 📈 **Unidad Indexada (UI)**
- **Fuente**: Instituto Nacional de Estadística (INE)
- **Datos**: 23 años de historia (2002-2025)
- **Endpoints**: 4 endpoints REST
- **Funcionalidad**: Consultas por fecha/rango, búsqueda inteligente

### 💰 **Unidad Reajustable (UR)**
- **Fuente**: Banco Hipotecario del Uruguay (BHU)
- **Datos**: 56 años de historia (1969-2025)
- **Endpoints**: 6 endpoints REST
- **Funcionalidad**: Consultas por año/mes/rango, análisis histórico

### 💱 **Cotizaciones de Monedas**
- **Fuente**: Banco Central del Uruguay (BCU)
- **Datos**: 4 monedas (USD, EUR, ARS, BRL)
- **Endpoints**: 7 endpoints REST
- **Funcionalidad**: Cotizaciones actuales e históricas

---

## 🔄 Estado y Seguimiento

- Para cambios completados y releases: ver `CHANGELOG_2026-04-18.md` y `CHANGELOG_2025-10-11.md` (en la raíz del repositorio).
- Para continuidad operativa de corto plazo: ver `../NEXT_SESSION.md` y `./NEXT_SESSION.MD`.
- Para evolución de workflows y migración Node 24: ver `./ROADMAP_NODE24_ACTIONS.md`.

---

## 🤝 Contribuir

1. Lee la [Guía de Arquitectura](./ARCHITECTURE.md)
2. Revisa el [API Reference](./API_REFERENCE.md)
3. Sigue las [Mejores Prácticas](./FRONTEND_GUIDE.md#mejores-prácticas)
4. Ejecuta los tests antes de PR
5. Actualiza la documentación

---

## 📞 Contacto y Soporte

- **Documentación**: Revisa este directorio `docs/`
- **API Docs**: http://localhost:8000/api/docs
- **Issues**: Reporta problemas en el repositorio
- **Preguntas**: Consulta la documentación técnica

---

Esta documentación funciona como índice navegable. El detalle histórico y los planes de ejecución se mantienen en changelogs y documentos de continuidad para evitar desactualización del índice.
