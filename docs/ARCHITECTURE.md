# Arquitectura Técnica - SIFU

## 🏗️ Visión General de la Arquitectura

SIFU sigue un patrón de **Clean Architecture** con separación clara de responsabilidades:

```
┌─────────────────────────────────────────────────────────────┐
│                    🌐 PRESENTATION LAYER                    │
│                      (React Frontend)                       │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/REST
┌─────────────────────▼───────────────────────────────────────┐
│                   📡 API LAYER                              │
│                   (FastAPI)                                 │
├─────────────────────────────────────────────────────────────┤
│    UI Endpoints  │  UR Endpoints  │  Exchange Endpoints     │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  ⚙️ BUSINESS LOGIC LAYER                    │
│                   (Service Classes)                         │
├─────────────────────────────────────────────────────────────┤
│   UIService     │   URService    │   ExchangeRateService    │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  🔄 DATA PROCESSING LAYER                   │
│                   (Processor Classes)                       │
├─────────────────────────────────────────────────────────────┤
│  ExcelProcessor │ URExcelProcessor │ ExchangeRateProcessor  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   🗄️ DATA LAYER                             │
│                  (SQLAlchemy ORM)                           │
├─────────────────────────────────────────────────────────────┤
│  UIRecord       │  URRecord      │  ExchangeRateRecord      │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   💾 DATABASE                               │
│                   (SQLite)                                  │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Modelos de Datos

### 1. Modelos Pydantic (API Layer)

#### `UIValue`
```python
class UIValue:
    date: date          # Fecha del valor UI
    value: float        # Valor de la UI
    
    def dict() -> dict  # Serialización para API
```

#### `URValue`
```python
class URValue:
    year: int           # Año
    month: int          # Mes (1-12)
    value: float        # Valor de la UR
    
    def dict() -> dict  # Serialización para API
```

#### `ExchangeRateValue`
```python
class ExchangeRateValue:
    date: date          # Fecha de la cotización
    currency: str       # Código de moneda (USD, EUR, etc.)
    buy_rate: float     # Tasa de compra
    sell_rate: float    # Tasa de venta
    average_rate: float # Tasa promedio (opcional)
    arbitrage: str      # Fuente (BCU, etc.)
    
    def dict() -> dict  # Serialización para API
```

### 2. Modelos SQLAlchemy (Database Layer)

#### `UIRecord`
```sql
CREATE TABLE ui_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE UNIQUE NOT NULL,
    value FLOAT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_ui_date ON ui_records(date);
```

#### `URRecord`
```sql
CREATE TABLE ur_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    value FLOAT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, month)
);

-- Índices
CREATE INDEX idx_ur_year_month ON ur_records(year, month);
```

#### `ExchangeRateRecord`
```sql
CREATE TABLE exchange_rate_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    currency VARCHAR(10) NOT NULL,
    buy_rate FLOAT NOT NULL,
    sell_rate FLOAT NOT NULL,
    average_rate FLOAT,
    arbitrage VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, currency)
);

-- Índices
CREATE INDEX idx_exchange_date ON exchange_rate_records(date);
CREATE INDEX idx_exchange_currency ON exchange_rate_records(currency);
CREATE INDEX idx_exchange_date_currency ON exchange_rate_records(date, currency);
```

## ⚙️ Capa de Servicios (Business Logic)

### `UIService`
**Responsabilidad**: Lógica de negocio para Unidad Indexada

```python
class UIService:
    # Consultas básicas
    def get_latest() -> UIValue
    def get_by_date(date: date) -> UIValue
    def get_by_date_range(start: date, end: date) -> List[UIValue]
    
    # Búsqueda inteligente
    def find_closest_date(target_date: date) -> UIValue
    
    # Estadísticas
    def get_record_count() -> int
    def get_date_range() -> Tuple[date, date]
    
    # Análisis
    def calculate_variation(start: date, end: date) -> float
```

### `URService`
**Responsabilidad**: Lógica de negocio para Unidad Reajustable

```python
class URService:
    # Consultas básicas
    def get_latest() -> URValue
    def get_by_year_month(year: int, month: int) -> URValue
    def get_by_year(year: int) -> List[URValue]
    def get_by_range(start_year: int, start_month: int, 
                    end_year: int, end_month: int) -> List[URValue]
    
    # Búsqueda inteligente
    def find_closest_month(year: int, month: int) -> URValue
    
    # Estadísticas
    def get_info() -> Dict[str, Any]
    def get_available_years() -> List[int]
    
    # Análisis
    def calculate_yearly_variation(year: int) -> float
```

### `ExchangeRateService`
**Responsabilidad**: Lógica de negocio para Cotizaciones de Monedas

```python
class ExchangeRateService:
    # Consultas básicas
    def get_latest(currency: str = None) -> List[ExchangeRateValue]
    def get_by_date(date: date, currency: str = None) -> List[ExchangeRateValue]
    def get_currency_history(currency: str, limit: int = 30) -> List[ExchangeRateValue]
    def get_by_date_range(start: date, end: date) -> List[ExchangeRateValue]
    
    # Búsqueda específica
    def get_specific_rate(date: date, currency: str) -> ExchangeRateValue
    def find_closest_date(target_date: date, currency: str = None) -> List[ExchangeRateValue]
    
    # Estadísticas y metadatos
    def get_info() -> Dict[str, Any]
    def get_available_currencies() -> List[str]
    def get_currency_stats(currency: str) -> Dict[str, Any]
```

## 🔄 Capa de Procesamiento de Datos

### `ExcelProcessor` (UI Data)
**Responsabilidad**: Procesamiento de datos del INE (Excel)

```python
class ExcelProcessor:
    def download_ui_data() -> str
    def process_ui_excel(file_path: str) -> List[UIValue]
    def parse_ui_date(date_str: str) -> date
    def parse_ui_value(value_str: str) -> float
    def save_ui_records(records: List[UIValue]) -> int
```

**Fuente de Datos**: 
- URL: `https://www5.ine.gub.uy/documents/Estad%C3%ADsticasecon%C3%B3micas/SERIES%20Y%20OTROS/UI/Unidad%20Indexada.xls`
- Formato: Excel (.xls)
- Estructura: Fecha | Valor UI

### `URExcelProcessor` (UR Data)
**Responsabilidad**: Procesamiento de datos del BHU (Excel)

```python
class URExcelProcessor:
    def download_ur_data() -> str
    def process_ur_excel(file_path: str) -> List[URValue]
    def parse_ur_sheet(sheet) -> List[URValue]
    def save_ur_records(records: List[URValue]) -> int
```

**Fuente de Datos**:
- URL: `https://www.bhu.com.uy/documents/20126/40519/UNIDAD+REAJUSTABLE+HIST%C3%93RICA.xlsx`
- Formato: Excel (.xlsx)
- Estructura: Matriz Año/Mes con valores UR

### `ExchangeRateProcessor` (Exchange Rates)
**Responsabilidad**: Procesamiento de cotizaciones del BCU (HTML)

```python
class ExchangeRateProcessor:
    def fetch_bcu_rates() -> List[ExchangeRateValue]
    def parse_bcu_html(html_content: str) -> List[ExchangeRateValue]
    def parse_currency_pattern(text: str) -> Tuple[str, float, float]
    def create_sample_data() -> List[ExchangeRateValue]
    def save_exchange_records(records: List[ExchangeRateValue]) -> int
```

**Fuente de Datos**:
- URL: `https://www.bcu.gub.uy/`
- Formato: HTML (scraping con BeautifulSoup)
- Monedas: USD, EUR, ARS, BRL
- Fallback: Datos de muestra si no se puede acceder al BCU

## 📡 Capa de API (FastAPI)

### Endpoints de Sistema
```python
GET  /api/health                    # Health check
GET  /api/info                      # Información general
```

### Endpoints UI (Unidad Indexada)
```python
GET  /api/ui/latest                 # Último valor
GET  /api/ui/{date}                 # Por fecha específica
GET  /api/ui/range/{start}/{end}    # Por rango de fechas
POST /api/refresh                   # Actualizar datos desde INE
```

### Endpoints UR (Unidad Reajustable)
```python
GET  /api/ur/latest                                    # Último valor
GET  /api/ur/info                                      # Información de datos
GET  /api/ur/year-month/{year}/{month}                 # Por año y mes
GET  /api/ur/year/{year}                               # Por año completo
GET  /api/ur/range/{sy}/{sm}/{ey}/{em}                 # Por rango
POST /api/ur/refresh                                   # Actualizar desde BHU
```

### Endpoints Exchange Rates (Cotizaciones)
```python
GET  /api/exchange-rate/latest                         # Últimas cotizaciones
GET  /api/exchange-rate/info                           # Información
GET  /api/exchange-rate/currency/{currency}            # Por moneda
GET  /api/exchange-rate/{date}                         # Por fecha
GET  /api/exchange-rate/{date}/{currency}              # Específica
GET  /api/exchange-rate/range/{start}/{end}            # Por rango
POST /api/exchange-rate/refresh                        # Actualizar desde BCU
```

## 🎯 Patrones de Diseño Aplicados

### 1. **Repository Pattern**
- Separación entre lógica de negocio y acceso a datos
- Services actúan como repositories especializados

### 2. **Dependency Injection**
- FastAPI maneja automáticamente las dependencias
- Database sessions inyectadas en endpoints

### 3. **Strategy Pattern**
- Diferentes processors para diferentes fuentes de datos
- ExcelProcessor vs URExcelProcessor vs ExchangeRateProcessor

### 4. **Factory Pattern**
- Creación de modelos a partir de datos raw
- Processors crean objetos Value a partir de datos externos

### 5. **Adapter Pattern**
- Adaptación de datos externos a modelos internos
- Conversion entre formatos Excel/HTML → Python objects

## 🔒 Manejo de Errores y Validación

### Validación de Entrada
```python
# Pydantic models para validación automática
class UIRangeRequest(BaseModel):
    start_date: date = Field(..., description="Fecha de inicio")
    end_date: date = Field(..., description="Fecha de fin")
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date debe ser mayor que start_date')
        return v
```

### Respuestas Estandarizadas
```python
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None
```

### Manejo de Excepciones
```python
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"success": False, "message": str(exc)}
    )
```

## 📊 Optimizaciones de Performance

### 1. **Database Indexing**
- Índices en campos de búsqueda frecuente (date, currency)
- Constraints únicos para prevenir duplicados

### 2. **Caching Strategy**
- SQLite en memoria para consultas frecuentes
- Lazy loading de datos no utilizados

### 3. **Data Processing**
- Procesamiento por lotes (batch processing)
- Validación temprana de datos

### 4. **API Optimization**
- Response models optimizados
- Paginación en endpoints que retornan listas grandes

## 🧪 Estrategia de Testing

### Unit Tests
```python
# Servicios
test_ui_service.py
test_ur_service.py
test_exchange_rate_service.py

# Procesadores
test_excel_processor.py
test_ur_excel_processor.py
test_exchange_rate_processor.py

# API Endpoints
test_api_endpoints.py
```

### Integration Tests
```python
# Test completo del flujo
test_data_pipeline.py
test_api_integration.py
```

### Test Data Strategy
- Fixtures con datos de muestra
- Mocking de servicios externos
- Database temporal para tests

## 🔄 Flujo de Datos Completo

```
1. 📥 DATA INGESTION
   ├── INE Excel Download → UI Data
   ├── BHU Excel Download → UR Data
   └── BCU HTML Scraping → Exchange Rates

2. 🔄 PROCESSING
   ├── Excel Parsing (pandas)
   ├── HTML Parsing (BeautifulSoup)
   └── Data Validation (Pydantic)

3. 💾 STORAGE
   ├── SQLAlchemy ORM
   ├── Batch Inserts/Updates
   └── Conflict Resolution

4. 📡 API LAYER
   ├── FastAPI Endpoints
   ├── Response Formatting
   └── Error Handling

5. 🌐 FRONTEND
   ├── React Components
   ├── State Management
   └── User Interface
```

## 📈 Escalabilidad y Mantenimiento

### Horizontal Scaling
- Stateless API design
- Database connection pooling
- Containerized deployment

### Vertical Scaling
- Optimized queries
- Efficient data structures
- Memory management

### Maintenance
- Modular architecture
- Clear separation of concerns
- Comprehensive documentation
- Automated testing

---

Este documento describe la arquitectura técnica completa del sistema. Para información de uso y deployment, consulta el [README.md](../README.md) principal. 