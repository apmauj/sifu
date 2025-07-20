# SIFU - Sistema de Índices Financieros del Uruguay

Sistema web para consulta de índices financieros y tasas de cambio en Uruguay.

## 🚀 Características

- **Backend**: FastAPI con Python
- **Frontend**: React con Vite
- **Base de Datos**: PostgreSQL
- **Contenedores**: Docker y Docker Compose
- **Internacionalización**: Soporte multiidioma (ES, EN, PT)

## 📋 Prerrequisitos

- Docker y Docker Compose
- Node.js 18+ (para desarrollo local)
- Python 3.9+ (para desarrollo local)

## 🛠️ Instalación y Uso

### Con Docker (Recomendado)

```bash
# Clonar el repositorio
git clone <tu-repositorio>
cd sifu

# Iniciar todos los servicios
docker-compose up -d

# Acceder a la aplicación
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Gateway: http://localhost:8080
```

### Desarrollo Local (Windows)

```powershell
# Backend
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend (en otra terminal)
cd frontend
npm install
npm run dev
```

## 📁 Estructura del Proyecto

```
sifu/
├── backend/                 # FastAPI backend
│   ├── main.py             # Punto de entrada
│   ├── requirements.txt    # Dependencias Python
│   └── ...
├── frontend/               # React frontend
│   ├── src/
│   ├── package.json
│   └── ...
├── docker-compose.yml      # Configuración Docker
├── nginx.conf             # Configuración Nginx
└── README.md
```

## 🌐 Endpoints API

- `GET /api/exchange-rates` - Tasas de cambio
- `GET /api/brou-rates` - Tasas BROU
- `GET /api/ur-rates` - Tasas UR

## 🔧 Scripts Útiles

### PowerShell (Windows)

```powershell
# Iniciar todo el stack
.\start_app.ps1

# Solo backend
.\run_backend.ps1

# Solo frontend
.\run_frontend.ps1

# Detener servicios
.\stop_services.ps1
```

## 🐳 Docker

### Servicios Disponibles

- **backend**: FastAPI en puerto 8000
- **frontend**: React en puerto 3000
- **gateway**: Nginx proxy en puerto 8080
- **database**: PostgreSQL (opcional)

### Comandos Docker

```bash
# Construir imágenes
docker-compose build

# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down

# Reconstruir sin cache
docker-compose build --no-cache
```

## 🌍 Internacionalización

El proyecto soporta múltiples idiomas:
- Español (ES)
- Inglés (EN)
- Portugués (PT)

Los archivos de traducción se encuentran en:
- Frontend: `frontend/src/i18n/locales/`
- Backend: `static/i18n/`

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📊 Monitoreo

- **Health Check**: `GET /health`
- **API Docs**: `GET /docs` (Swagger UI)
- **ReDoc**: `GET /redoc`

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si encuentras algún problema o tienes preguntas, por favor abre un issue en el repositorio.

---

**Desarrollado con ❤️ para Uruguay** 