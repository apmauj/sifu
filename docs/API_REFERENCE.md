# API Reference - SIFU

## 📡 Base URL
```
http://localhost:8000/api
```

## 🔧 Autenticación
- **Tipo**: No requiere autenticación
- **Headers**: `Content-Type: application/json`

## 📋 Estructura de Respuesta

### Respuesta Exitosa
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { ... }
}
```

### Respuesta de Error
```json
{
  "success": false,
  "message": "Error description",
  "error": "Detailed error message"
}
```

---

## 🏠 Endpoints del Sistema

### Health Check
```http
GET /api/health
```

**Descripción**: Verificar el estado del servicio

**Respuesta**:
```json
{
  "success": true,
  "message": "API is healthy",
  "data": {
    "status": "ok",
    "timestamp": "2025-06-16T10:30:00Z"
  }
}
```

### Información General
```http
GET /api/info
```

**Descripción**: Información general del sistema

**Respuesta**:
```json
{
  "success": true,
  "message": "System info retrieved",
  "data": {
    "ui_records": 8436,
    "ur_records": 676,
    "exchange_records": 5,
    "last_updated": "2025-06-16T10:30:00Z"
  }
}
```

---

## 📈 Endpoints de Unidad Indexada (UI)

### Obtener Último Valor
```http
GET /api/ui/latest
```

**Descripción**: Obtiene el último valor disponible de UI

**Respuesta**:
```json
{
  "success": true,
  "message": "Latest UI value retrieved",
  "data": {
    "date": "2025-06-15",
    "value": 7.152634
  }
}
```

### Obtener UI por Fecha
```http
GET /api/ui/{date}
```

**Parámetros**:
- `date` (string): Fecha en formato YYYY-MM-DD

**Ejemplo**:
```http
GET /api/ui/2025-06-15
```

**Respuesta**:
```json
{
  "success": true,
  "message": "UI value for 2025-06-15 retrieved",
  "data": {
    "date": "2025-06-15",
    "value": 7.152634
  }
}
```

### Obtener UI por Rango de Fechas
```http
GET /api/ui/range/{start_date}/{end_date}
```

**Parámetros**:
- `start_date` (string): Fecha inicio en formato YYYY-MM-DD
- `end_date` (string): Fecha fin en formato YYYY-MM-DD

**Ejemplo**:
```http
GET /api/ui/range/2025-06-01/2025-06-15
```

**Respuesta**:
```json
{
  "success": true,
  "message": "UI values for range retrieved",
  "data": [
    {
      "date": "2025-06-01",
      "value": 7.145123
    },
    {
      "date": "2025-06-02",
      "value": 7.146789
    }
  ]
}
```

### Actualizar Datos UI
```http
POST /api/refresh
```

**Descripción**: Actualiza los datos de UI desde el INE

**Respuesta**:
```json
{
  "success": true,
  "message": "UI data refreshed successfully",
  "data": {
    "records_processed": 15,
    "records_updated": 5,
    "last_update": "2025-06-16T10:30:00Z"
  }
}
```

---

## 💰 Endpoints de Unidad Reajustable (UR)

### Obtener Último Valor UR
```http
GET /api/ur/latest
```

**Respuesta**:
```json
{
  "success": true,
  "message": "Latest UR value retrieved",
  "data": {
    "year": 2025,
    "month": 6,
    "value": 6813.29
  }
}
```

### Obtener Información de Datos UR
```http
GET /api/ur/info
```

**Respuesta**:
```json
{
  "success": true,
  "message": "UR info retrieved",
  "data": {
    "total_records": 676,
    "first_record": {
      "year": 1969,
      "month": 3
    },
    "last_record": {
      "year": 2025,
      "month": 6
    },
    "available_years": [1969, 1970, "...", 2025]
  }
}
```

### Obtener UR por Año y Mes
```http
GET /api/ur/year-month/{year}/{month}
```

**Parámetros**:
- `year` (integer): Año (ej: 2025)
- `month` (integer): Mes (1-12)

**Ejemplo**:
```http
GET /api/ur/year-month/2025/6
```

**Respuesta**:
```json
{
  "success": true,
  "message": "UR value for 2025/6 retrieved",
  "data": {
    "year": 2025,
    "month": 6,
    "value": 6813.29
  }
}
```

### Obtener UR por Año Completo
```http
GET /api/ur/year/{year}
```

**Parámetros**:
- `year` (integer): Año (ej: 2025)

**Ejemplo**:
```http
GET /api/ur/year/2025
```

**Respuesta**:
```json
{
  "success": true,
  "message": "UR values for year 2025 retrieved",
  "data": [
    {
      "year": 2025,
      "month": 1,
      "value": 6750.15
    },
    {
      "year": 2025,
      "month": 2,
      "value": 6781.92
    }
  ]
}
```

### Obtener UR por Rango
```http
GET /api/ur/range/{start_year}/{start_month}/{end_year}/{end_month}
```

**Parámetros**:
- `start_year` (integer): Año inicio
- `start_month` (integer): Mes inicio (1-12)
- `end_year` (integer): Año fin
- `end_month` (integer): Mes fin (1-12)

**Ejemplo**:
```http
GET /api/ur/range/2024/12/2025/6
```

**Respuesta**:
```json
{
  "success": true,
  "message": "UR values for range retrieved",
  "data": [
    {
      "year": 2024,
      "month": 12,
      "value": 6720.45
    },
    {
      "year": 2025,
      "month": 1,
      "value": 6750.15
    }
  ]
}
```

### Actualizar Datos UR
```http
POST /api/ur/refresh
```

**Query Parameters** (opcionales):
- `use_sample_data` (boolean): Usar datos de muestra (default: false)

**Ejemplo**:
```http
POST /api/ur/refresh?use_sample_data=true
```

**Respuesta**:
```json
{
  "success": true,
  "message": "UR data refreshed successfully",
  "data": {
    "records_processed": 12,
    "records_updated": 3,
    "source": "BHU Excel",
    "last_update": "2025-06-16T10:30:00Z"
  }
}
```

---

## 💱 Endpoints de Cotizaciones de Monedas

### Obtener Últimas Cotizaciones
```http
GET /api/exchange-rate/latest
```

**Query Parameters** (opcionales):
- `currency` (string): Filtrar por moneda específica (USD, EUR, ARS, BRL, CLP, PYG)

**Ejemplo**:
```http
GET /api/exchange-rate/latest?currency=USD
```

**Respuesta**:
```json
{
  "success": true,
  "message": "Latest exchange rates retrieved",
  "data": [
    {
      "date": "2025-06-16",
      "currency": "USD",
      "buy_rate": 42.50,
      "sell_rate": 43.50,
      "average_rate": 43.00,
      "arbitrage": "BCU"
    },
    {
      "date": "2025-06-16",
      "currency": "EUR",
      "buy_rate": 45.20,
      "sell_rate": 46.30,
      "average_rate": 45.75,
      "arbitrage": "BCU"
    }
  ]
}
```

### Obtener Información de Cotizaciones
```http
GET /api/exchange-rate/info
```

**Respuesta**:
```json
{
  "success": true,
  "message": "Exchange rate info retrieved",
  "data": {
    "total_records": 30,
    "available_currencies": ["USD", "EUR", "ARS", "BRL", "CLP"],
    "date_range": {
      "first_date": "2025-06-01",
      "last_date": "2025-06-16"
    },
    "last_update": "2025-06-16T10:30:00Z"
  }
}
```

### Obtener Historial por Moneda
```http
GET /api/exchange-rate/currency/{currency}
```

**Parámetros**:
- `currency` (string): Código de moneda (USD, EUR, ARS, BRL, CLP, PYG)

**Query Parameters** (opcionales):
- `limit` (integer): Número máximo de registros (default: 30)

**Ejemplo**:
```http
GET /api/exchange-rate/currency/USD?limit=10
```

**Respuesta**:
```json
{
  "success": true,
  "message": "USD exchange rate history retrieved",
  "data": [
    {
      "date": "2025-06-16",
      "currency": "USD",
      "buy_rate": 42.50,
      "sell_rate": 43.50,
      "average_rate": 43.00,
      "arbitrage": "BCU"
    },
    {
      "date": "2025-06-15",
      "currency": "USD",
      "buy_rate": 42.30,
      "sell_rate": 43.20,
      "average_rate": 42.75,
      "arbitrage": "BCU"
    }
  ]
}
```

### Obtener Cotizaciones por Fecha
```http
GET /api/exchange-rate/{date}
```

**Parámetros**:
- `date` (string): Fecha en formato YYYY-MM-DD

**Query Parameters** (opcionales):
- `currency` (string): Filtrar por moneda específica

**Ejemplo**:
```http
GET /api/exchange-rate/2025-06-16?currency=USD
```

**Respuesta**:
```json
{
  "success": true,
  "message": "Exchange rates for 2025-06-16 retrieved",
  "data": [
    {
      "date": "2025-06-16",
      "currency": "USD",
      "buy_rate": 42.50,
      "sell_rate": 43.50,
      "average_rate": 43.00,
      "arbitrage": "BCU"
    }
  ]
}
```

### Obtener Cotización Específica
```http
GET /api/exchange-rate/{date}/{currency}
```

**Parámetros**:
- `date` (string): Fecha en formato YYYY-MM-DD
- `currency` (string): Código de moneda

**Ejemplo**:
```http
GET /api/exchange-rate/2025-06-16/USD
```

**Respuesta**:
```json
{
  "success": true,
  "message": "USD exchange rate for 2025-06-16 retrieved",
  "data": {
    "date": "2025-06-16",
    "currency": "USD",
    "buy_rate": 42.50,
    "sell_rate": 43.50,
    "average_rate": 43.00,
    "arbitrage": "BCU"
  }
}
```

### Obtener Cotizaciones por Rango de Fechas
```http
GET /api/exchange-rate/range/{start_date}/{end_date}
```

**Parámetros**:
- `start_date` (string): Fecha inicio en formato YYYY-MM-DD
- `end_date` (string): Fecha fin en formato YYYY-MM-DD

**Query Parameters** (opcionales):
- `currency` (string): Filtrar por moneda específica

**Ejemplo**:
```http
GET /api/exchange-rate/range/2025-06-01/2025-06-16?currency=USD
```

**Respuesta**:
```json
{
  "success": true,
  "message": "Exchange rates for range retrieved",
  "data": [
    {
      "date": "2025-06-01",
      "currency": "USD",
      "buy_rate": 41.80,
      "sell_rate": 42.90,
      "average_rate": 42.35,
      "arbitrage": "BCU"
    },
    {
      "date": "2025-06-16",
      "currency": "USD",
      "buy_rate": 42.50,
      "sell_rate": 43.50,
      "average_rate": 43.00,
      "arbitrage": "BCU"
    }
  ]
}
```

### Actualizar Cotizaciones
```http
POST /api/exchange-rate/refresh
```

**Query Parameters** (opcionales):
- `use_sample_data` (boolean): Usar datos de muestra (default: false)

**Ejemplo**:
```http
POST /api/exchange-rate/refresh?use_sample_data=true
```

**Respuesta**:
```json
{
  "success": true,
  "message": "Exchange rates refreshed successfully",
  "data": {
    "records_processed": 5,
    "records_updated": 5,
    "source": "BCU Website",
    "currencies": ["USD", "EUR", "ARS", "BRL", "CLP"],
    "last_update": "2025-06-16T10:30:00Z"
  }
}
```

---

## 🚨 Códigos de Error HTTP

| Código | Significado | Descripción |
|--------|-------------|-------------|
| 200 | OK | Solicitud exitosa |
| 400 | Bad Request | Parámetros inválidos |
| 404 | Not Found | Recurso no encontrado |
| 422 | Unprocessable Entity | Error de validación |
| 500 | Internal Server Error | Error interno del servidor |

---

## 💱 Monedas Soportadas

| Código | Nombre | País |
|--------|--------|------|
| USD | Dólar Estadounidense | 🇺🇸 Estados Unidos |
| EUR | Euro | 🇪🇺 Unión Europea |
| ARS | Peso Argentino | 🇦🇷 Argentina |
| BRL | Real Brasileño | 🇧🇷 Brasil |
| CLP | Peso Chileno | 🇨🇱 Chile |
| PYG | Guaraní Paraguayo | 🇵🇾 Paraguay |

---

## 📝 Ejemplos de Uso

### JavaScript/Axios
```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api'
})

// Obtener últimas cotizaciones
const getLatestRates = async () => {
  try {
    const response = await api.get('/exchange-rate/latest')
    return response.data.data
  } catch (error) {
    console.error('Error:', error.response.data.message)
  }
}

// Obtener UI por fecha
const getUIValue = async (date) => {
  try {
    const response = await api.get(`/ui/${date}`)
    return response.data.data
  } catch (error) {
    console.error('Error:', error.response.data.message)
  }
}
```

### Python/Requests
```python
import requests

API_BASE = "http://localhost:8000/api"

# Obtener UR por año
def get_ur_by_year(year):
    try:
        response = requests.get(f"{API_BASE}/ur/year/{year}")
        response.raise_for_status()
        return response.json()["data"]
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# Actualizar datos
def refresh_exchange_rates():
    try:
        response = requests.post(f"{API_BASE}/exchange-rate/refresh")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
```

### cURL
```bash
# Obtener información del sistema
curl -X GET "http://localhost:8000/api/info" \
  -H "Content-Type: application/json"

# Obtener UI por rango
curl -X GET "http://localhost:8000/api/ui/range/2025-06-01/2025-06-16" \
  -H "Content-Type: application/json"

# Actualizar cotizaciones con datos de muestra
curl -X POST "http://localhost:8000/api/exchange-rate/refresh?use_sample_data=true" \
  -H "Content-Type: application/json"
```

---

Esta documentación cubre todos los endpoints disponibles en la API. Para obtener la documentación interactiva en tiempo real, visita: `http://localhost:8000/api/docs` 