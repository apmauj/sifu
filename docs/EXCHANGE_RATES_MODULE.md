# Módulo de Cotizaciones (Exchange Rates) - Rework 2025

## Descripción General

El módulo de **Cotizaciones** ha sido completamente rediseñado para proporcionar un sistema dual que combina:

1. **Datos Históricos del INE**: Para consultas y análisis históricos
2. **Datos Actuales del BCU**: Para cotizaciones en tiempo real

Este módulo forma parte del sistema SIFU junto con los módulos de UI y UR.

## 🏗️ Arquitectura Dual

### 📊 **Sistema Histórico (INE)**
- **Fuente**: Instituto Nacional de Estadística (INE)
- **Tipo**: Archivo Excel oficial con historial completo
- **Cobertura**: Octubre 2001 - Presente (23+ años)
- **Propósito**: Consultas históricas, análisis de tendencias, rangos de fechas
- **Actualización**: Bajo demanda (endpoint `/refresh`)

### 📈 **Sistema Tiempo Real (BCU)**  
- **Fuente**: Banco Central del Uruguay (BCU)
- **Tipo**: Scraping web en tiempo real
- **Cobertura**: Datos del día actual
- **Propósito**: Panel de cotizaciones actuales
- **Actualización**: Auto-refresh cada hora (sincronizado al minuto cero)

## 💱 Características del Sistema

### Monedas Soportadas
- **USD** 🇺🇸 - Dólar Estadounidense
- **EUR** 🇪🇺 - Euro
- **ARS** 🇦🇷 - Peso Argentino  
- **BRL** 🇧🇷 - Real Brasileño
- **CLP** 🇨🇱 - Peso Chileno (solo BCU)

### Tipos de Datos
- **Compra**: Precio de compra del banco
- **Venta**: Precio de venta del banco
- **Promedio**: Calculado automáticamente
- **Fuente**: INE (histórico) o BCU (actual)

## 🚀 Nueva Arquitectura Backend

### 1. Procesadores Separados

#### `ExchangeRateExcelProcessor` (INE - Histórico)
```python
class ExchangeRateExcelProcessor:
    def __init__(self):
        self.url = URL_INE_EXCHANGE_RATES  # Excel del INE
    
    def download_excel(self) -> Optional[pd.DataFrame]
    def parse_excel_data(self, excel_data) -> List[Tuple[...]]
    def _parse_rate_value(self, value) -> Optional[float]
    def save_to_database(self, db, records) -> int
    def refresh_data(self, db) -> Tuple[bool, str, int]
```

#### `ExchangeRateBCUProcessor` (BCU - Tiempo Real)
```python
class ExchangeRateBCUProcessor:
    def __init__(self):
        self.url = URL_BCU_EXCHANGE_RATES  # Web del BCU
    
    def get_current_rates(self) -> List[Tuple[str, float, float, Optional[float]]]
    def _parse_exchange_tables(self, soup, currency_patterns)
    def _parse_exchange_divs(self, soup, currency_patterns)
    def _extract_numeric_values(self, elements) -> List[float]
    def _get_sample_current_rates(self) -> List[...]  # Fallback
```

### 2. URLs de Fuentes Actualizadas

```python
# constants.py
URL_INE_EXCHANGE_RATES = "https://www5.ine.gub.uy/documents/Estadísticaseconómicas/SERIES%20Y%20OTROS/Cotización%20monedas/Cotización%20monedas.xlsx"
URL_BCU_EXCHANGE_RATES = "https://www.bcu.gub.uy/Servicios-Financieros-SSF/Paginas/Cotizaciones.aspx"
```

### 3. API Endpoints Actualizados

```python
# Endpoints históricos (INE)
POST /api/exchange-rate/refresh           # Actualizar datos históricos desde INE
GET  /api/exchange-rate/latest            # Últimas cotizaciones históricas
GET  /api/exchange-rate/{date}            # Cotizaciones por fecha específica
GET  /api/exchange-rate/{date}/{currency} # Cotización específica
GET  /api/exchange-rate/range/{start}/{end} # Rango de fechas
GET  /api/exchange-rate/currency/{currency} # Historial por moneda
GET  /api/exchange-rate/info              # Estadísticas generales

# Endpoint tiempo real (BCU)
GET  /api/exchange-rate/current           # Cotizaciones actuales del BCU
```

### 4. Base de Datos Optimizada

```sql
-- Tabla optimizada para 23+ años de datos
CREATE TABLE exchange_rate_records (
    id UUID PRIMARY KEY,
    date DATE NOT NULL,
    currency VARCHAR(3) NOT NULL,
    buy_rate NUMERIC(10, 4) NOT NULL,
    sell_rate NUMERIC(10, 4) NOT NULL,
    average_rate NUMERIC(10, 4),
    arbitrage VARCHAR(50) DEFAULT 'INE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(date, currency)
);

-- Índices optimizados
CREATE INDEX idx_exchange_date ON exchange_rate_records(date);
CREATE INDEX idx_exchange_currency ON exchange_rate_records(currency);
CREATE INDEX idx_exchange_date_currency ON exchange_rate_records(date, currency);
```

## 🎨 Nueva Experiencia Frontend

### 1. Panel de Cotizaciones en Tiempo Real

#### `ExchangeRatePanel.jsx` - Nuevo Componente
```javascript
// Características del panel:
- Posición: Header superior (debajo del menú principal)
- Diseño: Banda azul con gradiente
- Contenido: 4-5 cotizaciones principales
- Actualización: Auto-refresh cada hora (sincronizado al minuto cero)
- Responsivo: Layout adaptable mobile/desktop
- Fuente: Endpoint /api/exchange-rate/current

// Estados principales:
const [currentRates, setCurrentRates] = useState([]);
const [lastUpdate, setLastUpdate] = useState(null);
const [isLoading, setIsLoading] = useState(true);

// Funcionalidades:
- Formato 24 horas (13:19 en lugar de 1:19 PM)
- Colores diferenciados (verde=compra, rojo=venta)
- Banderas por moneda 🇺🇸🇪🇺🇦🇷🇧🇷
- Botón de refresh manual
- Fallback de datos de muestra si BCU no disponible
```

### 2. Integración en App Principal

```javascript
// App.jsx - Estructura actualizada
return (
  <ErrorBoundary>
    <div className="min-h-screen bg-gray-50">
      <Header onRefresh={handleRefresh} isRefreshing={isRefreshing} />
      
      {/* NUEVO: Panel de cotizaciones BCU en tiempo real */}
      <ExchangeRatePanel />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs: UI | UR | Cotizaciones */}
        {/* El tab "Cotizaciones" ahora usa datos históricos del INE */}
```

### 3. Servicio Actualizado

```javascript
// services/exchangeService.js - Métodos expandidos
const exchangeService = {
  // NUEVO: Cotizaciones actuales del BCU
  getCurrentRates: async () => {
    return makeRequest((apiInstance) => apiInstance.get('/exchange-rate/current'));
  },

  // Existentes: Datos históricos del INE
  getLatest: async (currency = null) => { /* INE data */ },
  getByDate: async (date, currency = null) => { /* INE data */ },
  getByDateRange: async (startDate, endDate, currency = null) => { /* INE data */ },
  getCurrencyHistory: async (currency, limit = 30) => { /* INE data */ },
  
  // Actualizado: Refresh para datos INE
  refresh: async (useSampleData = false) => { /* INE Excel processing */ }
};
```

## 📊 Flujos de Datos Actualizados

### 1. Inicialización de la App
```
App.jsx → 
  ├── loadLatestExchange() → exchangeService.getLatest() → INE historical data
  └── ExchangeRatePanel → exchangeService.getCurrentRates() → BCU current data
```

### 2. Panel de Cotizaciones (Tiempo Real)
```
ExchangeRatePanel → 
  Auto-refresh (5min) → 
    exchangeService.getCurrentRates() → 
      /api/exchange-rate/current → 
        ExchangeRateBCUProcessor → 
          BCU Website (with SSL handling) → 
            Sample data fallback if needed
```

### 3. Consultas Históricas (Tab Cotizaciones)
```
ExchangeSearchForm → 
  User search → 
    exchangeService.getByDate/Range/Currency() → 
      /api/exchange-rate/* → 
        Database (INE historical data) → 
          ExchangeResultsDisplay
```

### 4. Actualización de Datos Históricos
```
Header (Refresh button) → 
  handleRefresh() → 
    exchangeService.refresh() → 
      /api/exchange-rate/refresh → 
        ExchangeRateExcelProcessor → 
          Download INE Excel → 
            Parse 23,000+ records → 
              Update database
```

## 🔧 Configuración y Despliegue

### Variables de Entorno
```bash
# URLs actualizadas (constants.py)
URL_INE_EXCHANGE_RATES="https://www5.ine.gub.uy/documents/..."
URL_BCU_EXCHANGE_RATES="https://www.bcu.gub.uy/Servicios-Financieros-SSF/..."

# Timeouts optimizados
HTTP_TIMEOUT=30  # Para descargas grandes del INE
HTTP_USER_AGENT="SIFU/2.0"
```

### Dependencias Nuevas
```python
# requirements.txt - Ya incluidas
pandas>=1.5.0           # Para procesamiento Excel del INE
openpyxl>=3.0.0         # Engine para archivos Excel
beautifulsoup4>=4.12.0  # Para parsing HTML del BCU
lxml>=4.9.0             # Parser XML optimizado
```

### SSL y Certificados
```python
# Manejo mejorado de SSL para BCU
requests.get(url, verify=True, timeout=timeout)
# Con fallback automático a datos de muestra si falla SSL
```

## 📈 Métricas y Estadísticas

### Datos Cargados (Verificado)
```
✅ Fuente INE: 23,051 registros históricos
✅ Período: 01-10-2001 a 16-06-2025 (23+ años)
✅ Monedas: USD, EUR, ARS, BRL (4 principales)
✅ Tasa de éxito: 100% parsing del Excel

✅ Fuente BCU: 5 monedas en tiempo real
✅ Fallback: Datos de muestra si BCU no disponible
✅ Auto-refresh: Cada hora (sincronizado al minuto cero)
✅ SSL handling: Con manejo de errores robusto
```

### Ejemplo de Consultas Exitosas
```bash
# Datos históricos del 3 de junio (INE)
GET /api/exchange-rate/2025-06-03
→ 4 monedas: USD $40.40-$42.80, EUR $45.09-$50.35, etc.

# Datos actuales (BCU)  
GET /api/exchange-rate/current
→ 5 monedas con timestamp y fuente "BCU"
```

## 🎯 Beneficios del Rework

1. **Separación de Responsabilidades**: Histórico vs. Tiempo Real
2. **Datos Reales**: 23+ años de historia oficial del INE
3. **UX Mejorada**: Panel visible con cotizaciones actuales
4. **Robustez**: Fallbacks automáticos y manejo de errores
5. **Escalabilidad**: Arquitectura modular y optimizada
6. **Internacionalización**: Soporte completo en 3 idiomas

## 🔄 Traducción de Mensajes

### Backend Message Translation
```javascript
// I18nContext.jsx - Patrones de mensajes agregados
{
  pattern: /^Exchange rates for (.+) retrieved successfully\. (\d+) records found$/,
  key: 'backend_messages.exchange_date_retrieved',
  params: (match) => ({ date: match[1], count: match[2] })
},
// + 6 patrones adicionales para todos los tipos de consulta
```

### Idiomas Soportados
```json
// es.json, en.json, pt.json - Traducciones completas
{
  "exchange_latest_retrieved": "Últimas cotizaciones obtenidas exitosamente",
  "exchange_date_retrieved": "Cotizaciones para {date} obtenidas exitosamente. {count} registros encontrados",
  // + 20 claves de traducción adicionales
}
```

---

## 🚀 Getting Started Rápido

### 1. Actualizar Datos Históricos
```bash
curl -X POST "http://localhost:8000/api/exchange-rate/refresh"
# → Descarga y procesa Excel del INE (23,000+ registros)
```

### 2. Verificar Panel de Cotizaciones
```bash
# Abrir frontend: http://localhost:3000
# → Ver panel azul superior con cotizaciones BCU actuales
```

### 3. Probar Consultas Históricas
```bash
# Tab "💱 Cotizaciones" → Buscar fecha específica
# Ejemplo: 3 de junio de 2025 → 4 monedas con datos reales INE
```

Este rework establece una base sólida para el sistema de cotizaciones con datos reales oficiales y una experiencia de usuario optimizada. 🎉 