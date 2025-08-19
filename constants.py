"""
Constants and configuration values for the SIFU application
"""
import os

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
# Prefer environment variables to define database location.
# DATABASE_PATH points to a SQLite file path (e.g., /app/data/ui_data.db)
# DATABASE_URL can override fully (e.g., postgresql://...)
DATABASE_PATH = os.getenv("DATABASE_PATH", "./ui_data.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH}")
DATABASE_CONNECT_ARGS = {"check_same_thread": False}

# Table names
TABLE_UI_RECORDS = "ui_records"
TABLE_UR_RECORDS = "ur_records"
TABLE_EXCHANGE_RATE_RECORDS = "exchange_rate_records"

# Column names (English for international standards)
COLUMN_UI_DATE = "date"
COLUMN_UI_VALUE = "value"
COLUMN_UR_YEAR = "year"
COLUMN_UR_MONTH = "month"
COLUMN_UR_VALUE = "value"
COLUMN_EXCHANGE_RATE_DATE = "date"  
COLUMN_EXCHANGE_RATE_CURRENCY = "currency"
COLUMN_EXCHANGE_RATE_BUY = "buy_rate"
COLUMN_EXCHANGE_RATE_SELL = "sell_rate"
COLUMN_EXCHANGE_RATE_AVERAGE = "average_rate"
COLUMN_EXCHANGE_RATE_ARBITRAGE = "arbitrage"
COLUMN_ID = "id"
COLUMN_CREATED_AT = "created_at"
COLUMN_UPDATED_AT = "updated_at"

# =============================================================================
# API CONFIGURATION
# =============================================================================
API_TITLE = "SIFU - Sistema de Índices Financieros del Uruguay"
API_DESCRIPTION = "API para consultar índices financieros de Uruguay: Unidad Indexada (UI), Unidad Reajustable (UR) y Cotizaciones de Monedas"
API_VERSION = "1.0.0"
API_DOCS_URL = "/api/docs"
API_REDOC_URL = "/api/redoc"

# CORS Configuration
# Avoid wildcard origins together with credentials. Default to no credentials.
# In production, set allowed origins explicitly via environment variable ALLOW_ORIGINS (comma-separated).
_env_origins = os.getenv("ALLOW_ORIGINS")
CORS_ALLOW_ORIGINS = [o.strip() for o in _env_origins.split(",") if o.strip()] if _env_origins else ["*"]
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]
CORS_ALLOW_CREDENTIALS = False

# Static files
STATIC_DIRECTORY = "static"
STATIC_MOUNT_PATH = "/static"
STATIC_NAME = "static"

# =============================================================================
# SCHEDULER (APScheduler) CONFIGURATION
# =============================================================================
# Enable/disable the background scheduler via env (default: enabled)
SCHEDULER_ENABLED = os.getenv("SIFU_SCHEDULER_ENABLED", "true").lower() in ("1", "true", "yes", "on")

# Timezone used by cron triggers (defaults to Montevideo)
SCHEDULER_TIMEZONE = os.getenv("TIMEZONE", "America/Montevideo")

# Cron expressions (standard 5-field: min hour day month weekday)
# Daily UI refresh at 02:00
CRON_UI_REFRESH = os.getenv("CRON_UI_REFRESH", "0 2 * * *")
# Daily Exchange historical refresh at 03:00
CRON_EXCHANGE_REFRESH = os.getenv("CRON_EXCHANGE_REFRESH", "0 3 * * *")
# Monthly UR refresh on day 1 at 04:00
CRON_UR_REFRESH = os.getenv("CRON_UR_REFRESH", "0 4 1 * *")

# Hourly health/check cron for Exchange (verifica y refresca si falta el día actual)
CRON_EXCHANGE_HOURLY_CHECK = os.getenv("CRON_EXCHANGE_HOURLY_CHECK", "0 * * * *")  # top of every hour
EXCHANGE_HOURLY_CHECK_ENABLED = os.getenv("EXCHANGE_HOURLY_CHECK_ENABLED", "true").lower() in ("1","true","yes","on")
EXCHANGE_HOURLY_CHECK_START_HOUR = int(os.getenv("EXCHANGE_HOURLY_CHECK_START_HOUR", "9"))   # local tz hour to start attempts
EXCHANGE_HOURLY_CHECK_END_HOUR = int(os.getenv("EXCHANGE_HOURLY_CHECK_END_HOUR", "18"))     # local tz hour to stop attempts

# =============================================================================
# API ENDPOINTS
# =============================================================================
# Health
ENDPOINT_HEALTH = "/api/health"

# UI Endpoints
ENDPOINT_UI_LATEST = "/api/ui/latest"
ENDPOINT_UI_BY_DATE = "/api/ui/{date}"
ENDPOINT_UI_RANGE = "/api/ui/range/{start_date}/{end_date}"
ENDPOINT_INFO = "/api/info"
ENDPOINT_REFRESH = "/api/refresh"

# UR Endpoints
ENDPOINT_UR_LATEST = "/api/ur/latest"
ENDPOINT_UR_BY_YEAR_MONTH = "/api/ur/year-month/{year}/{month}"
ENDPOINT_UR_BY_YEAR = "/api/ur/year/{year}"
ENDPOINT_UR_RANGE = "/api/ur/range/{start_year}/{start_month}/{end_year}/{end_month}"
ENDPOINT_UR_RANGE_POST = "/api/ur/range"
ENDPOINT_UR_REFRESH = "/api/ur/refresh"
ENDPOINT_UR_INFO = "/api/ur/info"


# Exchange Rate Endpoints
ENDPOINT_EXCHANGE_RATE_LATEST = "/api/exchange-rate/latest"
ENDPOINT_EXCHANGE_RATE_BY_DATE = "/api/exchange-rate/{date}"
ENDPOINT_EXCHANGE_RATE_BY_CURRENCY = "/api/exchange-rate/currency/{currency}"
ENDPOINT_EXCHANGE_RATE_BY_DATE_CURRENCY = "/api/exchange-rate/{date}/{currency}"
ENDPOINT_EXCHANGE_RATE_RANGE = "/api/exchange-rate/range/{start_date}/{end_date}"
ENDPOINT_EXCHANGE_RATE_REFRESH = "/api/exchange-rate/refresh"
ENDPOINT_EXCHANGE_RATE_INFO = "/api/exchange-rate/info"

# =============================================================================
# HTTP STATUS CODES
# =============================================================================
HTTP_200_OK = 200
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_500_INTERNAL_SERVER_ERROR = 500

# =============================================================================
# RESPONSE MESSAGES
# =============================================================================
# Success messages
MSG_LATEST_UI_SUCCESS = "Latest UI value retrieved successfully"
MSG_LATEST_UR_SUCCESS = "Latest UR value retrieved successfully"
MSG_UI_DATE_SUCCESS = "UI value for {date} retrieved successfully"
MSG_UR_YEAR_MONTH_SUCCESS = "UR value for {year}-{month:02d} retrieved successfully"
MSG_UI_RANGE_SUCCESS = "UI values for range {start_date} - {end_date} retrieved successfully. {count} records found"
MSG_UR_YEAR_SUCCESS = "Retrieved {count} UR values for year {year}"
MSG_UR_RANGE_SUCCESS = "Retrieved {count} UR values for range {start_year}-{start_month:02d} to {end_year}-{end_month:02d}"
MSG_LATEST_EXCHANGE_RATE_SUCCESS = "Latest exchange rates retrieved successfully"
MSG_EXCHANGE_RATE_DATE_SUCCESS = "Exchange rates for {date} retrieved successfully"
MSG_EXCHANGE_RATE_CURRENCY_SUCCESS = "Exchange rates for {currency} retrieved successfully"
MSG_EXCHANGE_RATE_RANGE_SUCCESS = "Exchange rates for range {start_date} - {end_date} retrieved successfully. {count} records found"

# Error messages
MSG_NO_UI_DATA = "No UI data available. Run /api/refresh to load data."
MSG_NO_UR_DATA = "No UR data available"
MSG_NO_UI_DATE_DATA = "No data for {date}. Showing closest previous value"
MSG_NO_UR_YEAR_MONTH_DATA = "No UR data available for {year}-{month:02d}"
MSG_NO_UR_YEAR_DATA = "No UR data available for year {year}"
MSG_NO_UR_RANGE_DATA = "No UR data available for range {start_year}-{start_month:02d} to {end_year}-{end_month:02d}"
MSG_NO_UI_FOUND = "No UI data found for {date} or previous dates"
MSG_NO_EXCHANGE_RATE_DATA = "No exchange rate data available. Run /api/exchange-rate/refresh to load data."
MSG_NO_EXCHANGE_RATE_DATE_DATA = "No exchange rate data for {date}. Showing closest previous value"
MSG_NO_EXCHANGE_RATE_CURRENCY_DATA = "No exchange rate data available for {currency}"

# Validation messages
MSG_INVALID_MONTH = "Month must be between 1 and 12"
MSG_INVALID_DATE_RANGE = "Start date must be less than or equal to end date"
MSG_INVALID_PERIOD_RANGE = "Start period must be before or equal to end period"

# System messages
MSG_INTERNAL_SERVER_ERROR = "Internal server error"
MSG_INTERNAL_ERROR = "Internal error: {error}"

# Health check
MSG_HEALTH_OK = "ok"

# =============================================================================
# DATA SOURCES
# =============================================================================
DATA_SOURCE_INE = "Instituto Nacional de Estadística - Uruguay"

# =============================================================================
# EXCEL PROCESSOR CONFIGURATION
# =============================================================================
# URLs
URL_INE_UI = "https://www5.ine.gub.uy/documents/Estad%C3%ADsticasecon%C3%B3micas/SERIES%20Y%20OTROS/UI/Unidad%20Indexada.xls"
URL_BHU_UR = "https://bhu.com.uy/sites/default/files/2024-01/historico-ur.xls"
URL_INE_EXCHANGE_RATES = "https://www5.ine.gub.uy/documents/Estadísticaseconómicas/SERIES%20Y%20OTROS/Cotización%20monedas/Cotización%20monedas.xlsx"  # INE Historical Exchange rates
URL_BCU_EXCHANGE_RATES = "https://www.bcu.gub.uy/Estadisticas-e-Indicadores/Paginas/Cotizaciones.aspx"  # BCU Current rates

# HTTP Configuration
HTTP_TIMEOUT = 30
HTTP_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Excel processing
EXCEL_ENGINE_XLS = 'xlrd'
DATE_FORMATS = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']

# UR Excel specific
UR_MONTH_NAMES = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 
                  'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'SETIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']

# Year validation
MIN_VALID_YEAR = 1900
MAX_VALID_YEAR = 2100

# Exchange Rate Configuration
SUPPORTED_CURRENCIES = ["USD", "EUR", "ARS", "BRL"]  # Main currencies (available in INE and BCU)
DEFAULT_CURRENCY = "USD"

# Exchange Rate Validation
MIN_EXCHANGE_RATE = 0.0001
MAX_EXCHANGE_RATE = 1000000
VALID_CURRENCY_CODES = ["USD", "EUR", "ARS", "BRL", "PYG", "UYU"]

# =============================================================================
# SCHEDULER CONFIGURATION
# =============================================================================
# Enable or disable background scheduler via env
SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "true").lower() == "true"
SCHEDULER_TIMEZONE = os.getenv("SCHEDULER_TIMEZONE", "UTC")

# Cron expressions (crontab format) for APScheduler
# Default: UI and Exchange refresh daily at 03:00 UTC; UR refresh on day 1 at 04:00 UTC
UI_REFRESH_CRON = os.getenv("UI_REFRESH_CRON", "0 3 * * *")
EXCHANGE_REFRESH_CRON = os.getenv("EXCHANGE_REFRESH_CRON", "0 3 * * *")
UR_REFRESH_CRON = os.getenv("UR_REFRESH_CRON", "0 4 1 * *")

# =============================================================================
# LOGGING MESSAGES
# =============================================================================
LOG_STARTING_APP = "🚀 Starting SIFU..."
LOG_NO_DATA_LOADING = "No data in database. Attempting to load initial data..."
LOG_INITIAL_DATA_LOADED = "✅ Initial data loaded: {count} records"
LOG_COULD_NOT_LOAD_DATA = "⚠️ Could not load initial data: {message}"
LOG_DATABASE_READY = "✅ Database ready with {count} records"

LOG_DOWNLOADING_EXCEL_INE = "Descargando archivo Excel desde INE..."
LOG_DOWNLOADING_EXCEL_BHU = "Descargando archivo Excel de UR desde BHU..."
LOG_EXCEL_DOWNLOADED = "Archivo descargado exitosamente. Filas: {count}"
LOG_EXCEL_UR_DOWNLOADED = "Archivo UR descargado exitosamente. Filas: {count}"
LOG_RECORDS_PARSED = "Parseados {count} registros válidos"
LOG_RECORDS_SAVED = "Guardados/actualizados {count} registros en la base de datos"

# =============================================================================
# RESPONSE FIELD NAMES
# =============================================================================
FIELD_SUCCESS = "success"
FIELD_MESSAGE = "message"
FIELD_DATA = "data"
FIELD_TOTAL_RECORDS = "total_records"
FIELD_LAST_UPDATED = "last_updated"
FIELD_STATUS = "status"
FIELD_TIMESTAMP = "timestamp"
FIELD_DATE = "date"
FIELD_VALUE = "value"
FIELD_YEAR = "year"
FIELD_MONTH = "month"
FIELD_DATE_RANGE = "date_range"
FIELD_MIN_DATE = "min_date"
FIELD_MAX_DATE = "max_date"
FIELD_LATEST_UI = "latest_ui"
FIELD_DATA_SOURCE = "data_source"
FIELD_YEAR_RANGE = "year_range"
FIELD_MIN_YEAR = "min_year"
FIELD_MAX_YEAR = "max_year"
FIELD_LATEST_VALUE = "latest_value"
FIELD_AVAILABLE_YEARS = "available_years"

# =============================================================================
# API TAG NAMES (for OpenAPI grouping) - keep Spanish originals for backward compatibility
# =============================================================================
TAG_UI = "Unidad Indexada (UI)"
TAG_UR = "Unidad Reajustable (UR)"
TAG_EXCHANGE = "Cotizaciones de Monedas"



# =============================================================================
# VALIDATION CONSTANTS
# =============================================================================
MIN_MONTH = 1
MAX_MONTH = 12 

# =============================================================================
# SCHEDULER SETTINGS (ENV-configurable)
# =============================================================================
SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "true").lower() == "true"
# Cron-like strings or simple presets for APScheduler triggers
SCHEDULE_UI_REFRESH_CRON = os.getenv("SCHEDULE_UI_REFRESH_CRON", "0 2 * * *")  # daily 02:00
SCHEDULE_EXCHANGE_REFRESH_CRON = os.getenv("SCHEDULE_EXCHANGE_REFRESH_CRON", "0 3 * * *")  # daily 03:00
SCHEDULE_UR_REFRESH_CRON = os.getenv("SCHEDULE_UR_REFRESH_CRON", "0 4 1 * *")  # monthly day 1 at 04:00

# Business day (weekday / optional holiday) filtering for scheduled refreshes
SCHEDULER_BUSINESS_DAY_ONLY = os.getenv("SCHEDULER_BUSINESS_DAY_ONLY", "true").lower() == "true"
# Comma-separated ISO dates (YYYY-MM-DD) of holidays where refresh should be skipped
_holidays_env = os.getenv("SCHEDULER_HOLIDAYS", "").strip()
SCHEDULER_HOLIDAYS = set([h for h in (x.strip() for x in _holidays_env.split(",")) if h])