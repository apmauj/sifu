# SIFU - Sistema de Índices Financieros del Uruguay

[![Deploy Frontend to GitHub Pages](https://github.com/apmauj/sifu/actions/workflows/deploy-frontend.yml/badge.svg)](https://github.com/apmauj/sifu/actions/workflows/deploy-frontend.yml)

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

### Probar el build de Pages en local

Para reproducir GitHub Pages (base "/sifu/") en local:

```powershell
# Construir
npm --prefix frontend run build

# Servir dist con base /sifu (usa un servidor simple)
npm --prefix frontend exec npx serve -s dist -l 5174
# Luego abre http://localhost:5174/sifu/
```

## 📁 Estructura del Proyecto

```text
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

Los archivos de traducción se sirven desde `frontend/public/i18n` en producción (Pages) y se incluyen fallbacks embebidos en `frontend/src/locales` por si el hosting no entrega `/i18n/*.json`.

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

### Desarrollado con ❤️ para Uruguay

---

### GitHub Pages

El frontend se publica automáticamente en GitHub Pages en cada push a `master` dentro de `frontend/`.

- URL: <https://apmauj.github.io/sifu/>
- Backend configurable con `VITE_PUBLIC_API_URL` (secret del repo) si no se sirve en `/sifu/api`.

Por qué no corre el backend en Pages: GitHub Pages solo sirve archivos estáticos. El backend (FastAPI/Python) debe hospedarse aparte y exponerse por HTTPS. Luego el frontend se construye con `VITE_PUBLIC_API_URL` apuntando a `https://TU-BACKEND/api`.

Guía: ver `docs/DEPLOY_BACKEND.md` para opciones rápidas (Render, VPS con Docker Compose o túnel temporal).
