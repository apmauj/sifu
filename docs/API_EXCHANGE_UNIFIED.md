# API Exchange - Terminología Unificada

## 📡 Base URL
```
http://localhost:8000/api
```

## 🎯 Objetivo
Esta documentación presenta la API de exchange con terminología unificada entre INE, BCU y BROU para mejorar la consistencia y usabilidad.

---

## 💱 Endpoints de Exchange Unificados

### 1. Cotizaciones Actuales (Tiempo Real)

#### Obtener Todas las Cotizaciones Actuales
```http
GET /api/exchange/current
```

**Descripción**: Obtiene cotizaciones actuales de todas las fuentes disponibles

**Respuesta**:
```json
{
  "success": true,
  "message": "Exchange rates retrieved successfully from BCU",
  "data": [
    {
      "currency": "USD",
      "buy_rate": 42.50,
      "sell_rate": 42.80,
      "average_rate": 42.65,
      "date": "2025-09-21",
      "source": "BCU",
      "source_type": "live",
      "timestamp": "2025-09-21T17:30:00Z",
      "is_preferential": false
    },
    {
      "currency": "EUR",
      "buy_rate": 46.20,
      "sell_rate": 46.50,
      "average_rate": 46.35,
      "date": "2025-09-21",
      "source": "BCU",
      "source_type": "live",
      "timestamp": "2025-09-21T17:30:00Z",
      "is_preferential": false
    }
  ],
  "metadata": {
    "total_records": 2,
    "source": "BCU",
    "source_type": "live",
    "source_description": "Banco Central del Uruguay",
    "timestamp": "2025-09-21T17:30:00Z",
    "currency_names": {
      "USD": "Dólar Estadounidense",
      "EUR": "Euro"
    }
  }
}
```

#### Obtener Cotizaciones por Fuente
```http
GET /api/exchange/current?source=BCU
GET /api/exchange/current?source=BROU
```

**Parámetros**:
- `source` (string, opcional): Filtrar por fuente específica (BCU, BROU, INE)

**Ejemplo - Solo BROU**:
```http
GET /api/exchange/current?source=BROU
```

**Respuesta**:
```json
{
  "success": true,
  "message": "Exchange rates retrieved successfully from BROU",
  "data": [
    {
      "currency": "USD",
      "buy_rate": 42.45,
      "sell_rate": 42.85,
      "average_rate": 42.65,
      "date": "2025-09-21",
      "source": "BROU",
      "source_type": "live",
      "timestamp": "2025-09-21T17:30:00Z",
      "is_preferential": false,
      "arbitrage_buy": 0.1234,
      "arbitrage_sell": 0.5678
    },
    {
      "currency": "USD_EBROU",
      "buy_rate": 43.10,
      "sell_rate": 43.40,
      "average_rate": 43.25,
      "date": "2025-09-21",
      "source": "BROU",
      "source_type": "live",
      "timestamp": "2025-09-21T17:30:00Z",
      "is_preferential": true,
      "arbitrage_buy": 0.2345,
      "arbitrage_sell": 0.6789
    }
  ],
  "metadata": {
    "total_records": 2,
    "source": "BROU",
    "source_type": "live",
    "source_description": "Banco República del Uruguay",
    "timestamp": "2025-09-21T17:30:00Z",
    "data_age_minutes": 15.5,
    "is_fresh": true,
    "status": {
      "label": "Datos en vivo",
      "color": "green",
      "description": "Cotizaciones obtenidas directamente del BROU"
    },
    "currency_names": {
      "USD": "Dólar Estadounidense",
      "USD_EBROU": "Dólar eBROU"
    }
  }
}
```

### 2. Cotizaciones Históricas

#### Obtener Últimas Cotizaciones Históricas
```http
GET /api/exchange/latest
```

**Descripción**: Obtiene las últimas cotizaciones históricas disponibles

**Respuesta**:
```json
{
  "success": true,
  "message": "Exchange rates retrieved successfully from INE",
  "data": [
    {
      "currency": "USD",
      "buy_rate": 42.30,
      "sell_rate": 42.60,
      "average_rate": 42.45,
      "date": "2025-09-20",
      "source": "INE",
      "source_type": "historical",
      "timestamp": "2025-09-20T23:59:59Z"
    }
  ],
  "metadata": {
    "total_records": 1,
    "source": "INE",
    "source_type": "historical",
    "source_description": "Instituto Nacional de Estadística",
    "timestamp": "2025-09-21T17:30:00Z",
    "currency_names": {
      "USD": "Dólar Estadounidense"
    }
  }
}
```

#### Obtener Cotizaciones por Fecha
```http
GET /api/exchange/{date}
```

**Parámetros**:
- `date` (string): Fecha en formato YYYY-MM-DD

**Ejemplo**:
```http
GET /api/exchange/2025-09-15
```

**Respuesta**:
```json
{
  "success": true,
  "message": "Exchange rates retrieved successfully from INE",
  "data": [
    {
      "currency": "USD",
      "buy_rate": 41.80,
      "sell_rate": 42.10,
      "average_rate": 41.95,
      "date": "2025-09-15",
      "source": "INE",
      "source_type": "historical",
      "timestamp": "2025-09-15T23:59:59Z"
    },
    {
      "currency": "EUR",
      "buy_rate": 45.50,
      "sell_rate": 45.80,
      "average_rate": 45.65,
      "date": "2025-09-15",
      "source": "INE",
      "source_type": "historical",
      "timestamp": "2025-09-15T23:59:59Z"
    }
  ],
  "metadata": {
    "total_records": 2,
    "source": "INE",
    "source_type": "historical",
    "source_description": "Instituto Nacional de Estadística",
    "timestamp": "2025-09-21T17:30:00Z",
    "currency_names": {
      "USD": "Dólar Estadounidense",
      "EUR": "Euro"
    }
  }
}
```

#### Obtener Cotizaciones por Rango de Fechas
```http
GET /api/exchange/range/{start_date}/{end_date}
```

**Parámetros**:
- `start_date` (string): Fecha inicio en formato YYYY-MM-DD
- `end_date` (string): Fecha fin en formato YYYY-MM-DD

**Ejemplo**:
```http
GET /api/exchange/range/2025-09-01/2025-09-15
```

**Respuesta**:
```json
{
  "success": true,
  "message": "Exchange rates retrieved successfully from INE",
  "data": [
    {
      "currency": "USD",
      "buy_rate": 41.50,
      "sell_rate": 41.80,
      "average_rate": 41.65,
      "date": "2025-09-01",
      "source": "INE",
      "source_type": "historical",
      "timestamp": "2025-09-01T23:59:59Z"
    },
    {
      "currency": "USD",
      "buy_rate": 41.80,
      "sell_rate": 42.10,
      "average_rate": 41.95,
      "date": "2025-09-15",
      "source": "INE",
      "source_type": "historical",
      "timestamp": "2025-09-15T23:59:59Z"
    }
  ],
  "metadata": {
    "total_records": 2,
    "source": "INE",
    "source_type": "historical",
    "source_description": "Instituto Nacional de Estadística",
    "timestamp": "2025-09-21T17:30:00Z",
    "currency_names": {
      "USD": "Dólar Estadounidense"
    }
  }
}
```

#### Obtener Historial por Moneda
```http
GET /api/exchange/currency/{currency}
```

**Parámetros**:
- `currency` (string): Código de moneda (USD, EUR, ARS, BRL, etc.)
- `limit` (int, opcional): Límite de registros (default: 30)

**Ejemplo**:
```http
GET /api/exchange/currency/USD?limit=10
```

**Respuesta**:
```json
{
  "success": true,
  "message": "Exchange rates retrieved successfully from INE",
  "data": [
    {
      "currency": "USD",
      "buy_rate": 42.50,
      "sell_rate": 42.80,
      "average_rate": 42.65,
      "date": "2025-09-21",
      "source": "INE",
      "source_type": "historical",
      "timestamp": "2025-09-21T23:59:59Z"
    },
    {
      "currency": "USD",
      "buy_rate": 42.30,
      "sell_rate": 42.60,
      "average_rate": 42.45,
      "date": "2025-09-20",
      "source": "INE",
      "source_type": "historical",
      "timestamp": "2025-09-20T23:59:59Z"
    }
  ],
  "metadata": {
    "total_records": 2,
    "source": "INE",
    "source_type": "historical",
    "source_description": "Instituto Nacional de Estadística",
    "timestamp": "2025-09-21T17:30:00Z",
    "currency_names": {
      "USD": "Dólar Estadounidense"
    }
  }
}
```

### 3. Información y Control

#### Obtener Información del Sistema
```http
GET /api/exchange/info
```

**Descripción**: Obtiene estadísticas e información del sistema de exchange

**Respuesta**:
```json
{
  "success": true,
  "message": "Exchange system info retrieved successfully",
  "data": {
    "total_records": 12543,
    "date_range": {
      "start": "2001-10-01",
      "end": "2025-09-21"
    },
    "currencies": [
      "USD",
      "EUR",
      "ARS",
      "BRL",
      "CLP"
    ],
    "sources": {
      "INE": {
        "records": 12450,
        "last_update": "2025-09-21T17:30:00Z",
        "description": "Instituto Nacional de Estadística"
      },
      "BCU": {
        "records": 93,
        "last_update": "2025-09-21T17:30:00Z",
        "description": "Banco Central del Uruguay"
      },
      "BROU": {
        "records": 0,
        "last_update": "2025-09-21T17:30:00Z",
        "description": "Banco República del Uruguay"
      }
    },
    "supported_currencies": {
      "USD": "Dólar Estadounidense",
      "EUR": "Euro",
      "ARS": "Peso Argentino",
      "BRL": "Real Brasileño",
      "CLP": "Peso Chileno"
    }
  }
}
```

#### Actualizar Datos
```http
POST /api/exchange/refresh
```

**Descripción**: Fuerza la actualización de datos desde las fuentes

**Respuesta**:
```json
{
  "success": true,
  "message": "Exchange data refresh initiated successfully",
  "data": {
    "refresh_id": "refresh_20250921_173000",
    "sources": ["INE", "BCU"],
    "estimated_duration": "2-5 minutes",
    "status": "in_progress"
  }
}
```

---

## 📋 Estructura de Datos Estandarizada

### Campos Obligatorios
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `currency` | string | Código de moneda ISO | "USD" |
| `buy_rate` | number | Tasa de compra | 42.50 |
| `sell_rate` | number | Tasa de venta | 42.80 |
| `average_rate` | number | Tasa promedio | 42.65 |
| `date` | string | Fecha de la cotización | "2025-09-21" |
| `source` | string | Fuente de datos | "BCU", "INE", "BROU" |
| `source_type` | string | Tipo de fuente | "live", "historical", "sample" |
| `timestamp` | string | Timestamp ISO | "2025-09-21T17:30:00Z" |

### Campos Opcionales
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `is_preferential` | boolean | Si es moneda preferencial | true |
| `arbitrage_buy` | number | Arbitraje de compra | 0.1234 |
| `arbitrage_sell` | number | Arbitraje de venta | 0.5678 |

### Metadatos
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `total_records` | number | Número total de registros |
| `source` | string | Fuente principal de datos |
| `source_type` | string | Tipo de fuente principal |
| `source_description` | string | Descripción de la fuente |
| `timestamp` | string | Timestamp de la consulta |
| `currency_names` | object | Nombres de monedas para display |
| `data_age_minutes` | number | Edad de los datos en minutos (BROU) |
| `is_fresh` | boolean | Si los datos son frescos (BROU) |
| `status` | object | Información de estado (BROU) |

---

## 🏷️ Códigos de Moneda Soportados

| Código | Nombre | Descripción |
|--------|--------|-------------|
| `USD` | Dólar Estadounidense | Moneda base |
| `USD_EBROU` | Dólar eBROU | Versión preferencial BROU |
| `EUR` | Euro | Unión Europea |
| `ARS` | Peso Argentino | Argentina |
| `BRL` | Real Brasileño | Brasil |
| `CLP` | Peso Chileno | Chile (solo BCU) |

---

## 🔗 Fuentes de Datos

| Fuente | Descripción | Tipo | Cobertura |
|--------|-------------|------|-----------|
| `BCU` | Banco Central del Uruguay | Tiempo real | Datos actuales |
| `INE` | Instituto Nacional de Estadística | Histórico | 2001-Presente |
| `BROU` | Banco República del Uruguay | Bancario | Cotizaciones bancarias |

---

## ⚠️ Manejo de Errores

### Respuesta de Error Estándar
```json
{
  "success": false,
  "message": "Error description",
  "data": null,
  "error": {
    "code": "EXCHANGE_ERROR",
    "timestamp": "2025-09-21T17:30:00Z",
    "details": {
      "source": "BCU",
      "error_type": "connection_timeout"
    }
  }
}
```

### Códigos de Error Comunes
- `EXCHANGE_ERROR`: Error general de exchange
- `SOURCE_UNAVAILABLE`: Fuente de datos no disponible
- `INVALID_CURRENCY`: Moneda no soportada
- `INVALID_DATE`: Formato de fecha inválido
- `NO_DATA`: No hay datos disponibles
- `RATE_LIMIT`: Límite de requests excedido

---

## 🚀 Casos de Uso Comunes

### 1. Panel de Cotizaciones Actuales
```javascript
// Obtener cotizaciones actuales de todas las fuentes
const response = await fetch('/api/exchange/current');
const data = await response.json();

// Filtrar por fuente específica
const brouRates = await fetch('/api/exchange/current?source=BROU');
```

### 2. Análisis Histórico
```javascript
// Obtener datos de los últimos 30 días
const endDate = new Date().toISOString().split('T')[0];
const startDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
const historical = await fetch(`/api/exchange/range/${startDate}/${endDate}`);
```

### 3. Seguimiento de Moneda Específica
```javascript
// Obtener historial de USD
const usdHistory = await fetch('/api/exchange/currency/USD?limit=100');
```

### 4. Verificación de Estado del Sistema
```javascript
// Verificar información del sistema
const systemInfo = await fetch('/api/exchange/info');
```

---

## 🔄 Migración desde API Anterior

### Cambios Principales
1. **Nombres de campos unificados**: `buy_rate`, `sell_rate`, `average_rate`
2. **Estructura de respuesta estandarizada**: Metadatos consistentes
3. **Endpoints unificados**: `/api/exchange/*` en lugar de múltiples rutas
4. **Terminología consistente**: Mismos nombres entre fuentes

### Compatibilidad
- ✅ **Backward compatible**: Endpoints antiguos siguen funcionando
- ✅ **Gradual migration**: Migración paso a paso
- ✅ **Documentation**: Guía de migración disponible
