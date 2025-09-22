# Análisis de Terminología Exchange - Unificación

## 🎯 Objetivo
Estandarizar y unificar la terminología entre INE, BCU y BROU en todos los endpoints de exchange para mejorar la consistencia y usabilidad de la API.

## 🔍 Análisis de Inconsistencias Actuales

### 1. **Endpoints Inconsistentes**

#### **BROU Endpoints**
```
GET /api/brou/current                    # Cotizaciones actuales BROU
GET /api/brou/current?full=true          # Con metadata adicional
```

#### **BCU/INE Exchange Endpoints**
```
GET /api/exchange-rate/latest            # Últimas cotizaciones históricas
GET /api/exchange-rate/current           # Cotizaciones actuales BCU
GET /api/exchange-rate/{date}            # Por fecha específica
GET /api/exchange-rate/{date}/{currency} # Cotización específica
GET /api/exchange-rate/range/{start}/{end} # Rango de fechas
GET /api/exchange-rate/currency/{currency} # Historial por moneda
GET /api/exchange-rate/info              # Estadísticas generales
POST /api/exchange-rate/refresh          # Actualizar datos históricos
```

### 2. **Estructura de Datos Inconsistente**

#### **BROU Response (Modo Completo)**
```json
{
  "success": true,
  "message": "Cotizaciones BROU obtenidas (4 monedas)",
  "data": [
    {
      "currency": "USD",
      "buy_rate": 42.50,
      "sell_rate": 42.80,
      "average_rate": 42.65,
      "arbitrage_buy": 0.1234,
      "arbitrage_sell": 0.5678,
      "preferential": false,
      "source": "BROU",
      "timestamp": "2025-09-21T17:30:00Z"
    }
  ],
  "source": "BROU",
  "source_type": "live",
  "status": {...},
  "timestamp": "2025-09-21T17:30:00Z",
  "data_age_minutes": 15.5,
  "is_fresh": true,
  "frontend_display": {...}
}
```

#### **BCU/INE Response (Típica)**
```json
{
  "success": true,
  "message": "Exchange rates retrieved successfully",
  "data": [
    {
      "currency": "USD",
      "buy": 42.50,
      "sell": 42.80,
      "average": 42.65,
      "date": "2025-09-21",
      "source": "BCU"
    }
  ]
}
```

### 3. **Nombres de Monedas Inconsistentes**

#### **BROU**
- `USD` - Dólar USA
- `USD_EBROU` - Dólar eBROU (preferencial)
- `EUR` - Euro
- `ARS` - Peso Argentino
- `BRL` - Real Brasileño

#### **BCU/INE**
- `USD` - Dólar Estadounidense
- `EUR` - Euro
- `ARS` - Peso Argentino
- `BRL` - Real Brasileño
- `CLP` - Peso Chileno (solo BCU)

### 4. **Terminología de Campos**

#### **Inconsistencias Identificadas**
| Campo | BROU | BCU/INE | Propuesta Unificada |
|-------|------|---------|-------------------|
| Compra | `buy_rate` | `buy` | `buy_rate` |
| Venta | `sell_rate` | `sell` | `sell_rate` |
| Promedio | `average_rate` | `average` | `average_rate` |
| Moneda | `currency` | `currency` | `currency` ✅ |
| Fecha | `timestamp` | `date` | `date` |
| Fuente | `source` | `source` | `source` ✅ |

### 5. **Fuentes de Datos**

#### **INE (Instituto Nacional de Estadística)**
- **Tipo**: Datos históricos
- **Formato**: Excel
- **Cobertura**: Octubre 2001 - Presente
- **Propósito**: Análisis histórico, consultas por fecha

#### **BCU (Banco Central del Uruguay)**
- **Tipo**: Datos en tiempo real
- **Formato**: Web scraping
- **Cobertura**: Datos del día actual
- **Propósito**: Cotizaciones actuales

#### **BROU (Banco República del Uruguay)**
- **Tipo**: Datos bancarios específicos
- **Formato**: Web scraping
- **Cobertura**: Cotizaciones bancarias
- **Propósito**: Operaciones bancarias, arbitraje

## 📋 Propuesta de Unificación

### 1. **Estructura de Response Unificada**

```json
{
  "success": true,
  "message": "Exchange rates retrieved successfully",
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
      "metadata": {
        "is_preferential": false,
        "arbitrage_buy": 0.1234,
        "arbitrage_sell": 0.5678
      }
    }
  ],
  "metadata": {
    "total_records": 1,
    "source": "BCU",
    "source_type": "live",
    "timestamp": "2025-09-21T17:30:00Z",
    "data_age_minutes": 15.5,
    "is_fresh": true
  }
}
```

### 2. **Nombres de Campos Estandarizados**

| Campo | Descripción | Tipo | Ejemplo |
|-------|-------------|------|---------|
| `currency` | Código de moneda ISO | string | "USD" |
| `buy_rate` | Tasa de compra | number | 42.50 |
| `sell_rate` | Tasa de venta | number | 42.80 |
| `average_rate` | Tasa promedio | number | 42.65 |
| `date` | Fecha de la cotización | string | "2025-09-21" |
| `source` | Fuente de datos | string | "BCU", "INE", "BROU" |
| `source_type` | Tipo de fuente | string | "live", "historical", "sample" |
| `timestamp` | Timestamp ISO | string | "2025-09-21T17:30:00Z" |

### 3. **Códigos de Moneda Estandarizados**

| Código | Nombre | Descripción |
|--------|--------|-------------|
| `USD` | Dólar Estadounidense | Moneda base |
| `USD_EBROU` | Dólar eBROU | Versión preferencial BROU |
| `EUR` | Euro | Unión Europea |
| `ARS` | Peso Argentino | Argentina |
| `BRL` | Real Brasileño | Brasil |
| `CLP` | Peso Chileno | Chile (solo BCU) |

### 4. **Tipos de Fuente Estandarizados**

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| `live` | Datos en tiempo real | BCU actual |
| `historical` | Datos históricos | INE, BCU histórico |
| `sample` | Datos de muestra | Fallback cuando falla la fuente |
| `persisted` | Datos almacenados | Caché de consultas anteriores |

### 5. **Endpoints Propuestos**

#### **Endpoints Unificados**
```
# Cotizaciones actuales (tiempo real)
GET /api/exchange/current                # Todas las fuentes
GET /api/exchange/current?source=BCU     # Solo BCU
GET /api/exchange/current?source=BROU    # Solo BROU

# Cotizaciones históricas
GET /api/exchange/latest                 # Últimas disponibles
GET /api/exchange/{date}                 # Por fecha específica
GET /api/exchange/range/{start}/{end}    # Por rango de fechas
GET /api/exchange/currency/{currency}    # Por moneda específica

# Información y control
GET /api/exchange/info                   # Estadísticas
POST /api/exchange/refresh               # Actualizar datos
```

## 🎯 Beneficios de la Unificación

### 1. **Para Desarrolladores**
- ✅ **API Consistente**: Misma estructura en todos los endpoints
- ✅ **Documentación Clara**: Terminología unificada
- ✅ **Ejemplos Reales**: Casos de uso prácticos
- ✅ **Mejor DX**: Developer Experience mejorada

### 2. **Para Usuarios**
- ✅ **Interfaz Consistente**: Misma experiencia en todos los paneles
- ✅ **Datos Confiables**: Fuentes claramente identificadas
- ✅ **Transparencia**: Metadatos completos sobre origen de datos

### 3. **Para el Sistema**
- ✅ **Mantenibilidad**: Código más fácil de mantener
- ✅ **Escalabilidad**: Estructura preparada para futuras fuentes
- ✅ **Testing**: Tests más consistentes y confiables

## 📝 Próximos Pasos

1. **Implementar estructura unificada** en todos los endpoints
2. **Actualizar documentación** con ejemplos reales
3. **Migrar frontend** a terminología unificada
4. **Crear tests** para validar consistencia
5. **Documentar migración** para usuarios existentes
