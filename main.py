from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import List, Optional
import logging
import uuid
import time
import os

from database import get_db
from models import UIResponse, RefreshResponse, UIValue, UIRangeRequest, URResponse, URRangeRequest, ExchangeRateResponse
from services import UIService, URService, ExchangeRateService
from excel_processor import ExcelProcessor, URExcelProcessor, ExchangeRateExcelProcessor, ExchangeRateBCUProcessor
from brou_processor import BROUProcessor
from constants import *

# APScheduler (background jobs)
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
    from apscheduler.triggers.cron import CronTrigger  # type: ignore
    import pytz  # type: ignore
else:
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
        from apscheduler.triggers.cron import CronTrigger  # type: ignore
        import pytz  # type: ignore
    except Exception:
        AsyncIOScheduler = None  # type: ignore
        CronTrigger = None  # type: ignore
        pytz = None  # type: ignore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application with improved documentation
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url=API_DOCS_URL,
    redoc_url=API_REDOC_URL,
    tags_metadata=[
        {
            "name": "🏠 Sistema",
            "description": "Endpoints de sistema: health check e información general"
        },
        {
            "name": "📈 Unidad Indexada (UI)",
            "description": "Consulta de valores de la Unidad Indexada del Instituto Nacional de Estadística (INE). "
                          "La UI es un índice de ajuste por inflación utilizado en Uruguay desde 2002."
        },
        {
            "name": "💰 Unidad Reajustable (UR)",
            "description": "Consulta de valores de la Unidad Reajustable del Banco Hipotecario del Uruguay (BHU). "
                          "La UR es un índice utilizado para reajustar créditos hipotecarios desde 1969."
        },
        {
            "name": "💱 Cotizaciones de Monedas",
            "description": "Sistema dual de cotizaciones: datos históricos del INE (2001-presente) y "
                          "cotizaciones actuales del BCU en tiempo real. Incluye USD, EUR, ARS, BRL."
        },
        {
            "name": "🏦 BROU",
            "description": "Cotizaciones del Banco de la República Oriental del Uruguay (BROU). "
                          "Incluye USD, USD eBROU, EUR, ARS, BRL con valores de compra/venta y arbitrajes."
        }
    ]
)

# Configure CORS to allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)

@app.get("/", tags=["🏠 Sistema"])
async def root_index():
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "docs": API_DOCS_URL,
        "health": ENDPOINT_HEALTH,
    }

# -----------------------------------------------------------------------------
# Scheduler setup (optional)
# -----------------------------------------------------------------------------
scheduler: Any = None

def _add_jobs(_scheduler):
    tz = pytz.timezone(SCHEDULER_TIMEZONE) if pytz else None

    # UI daily refresh
    def job_ui_refresh():
        try:
            from database import SessionLocal
            db = SessionLocal()
            logger.info("[Scheduler] Running UI refresh job...")
            success, message, total_records = excel_processor.refresh_data(db)
            logger.info(f"[Scheduler][UI] success={success} msg='{message}' total_records={total_records}")
            db.close()
        except Exception as e:
            logger.error(f"[Scheduler][UI] error: {e}")

    # Exchange historical daily refresh
    def job_exchange_refresh():
        try:
            from database import SessionLocal
            db = SessionLocal()
            logger.info("[Scheduler] Running Exchange refresh job...")
            success, message, total_records = exchange_rate_excel_processor.refresh_data(db)
            logger.info(f"[Scheduler][EXCHANGE] success={success} msg='{message}' total_records={total_records}")
            db.close()
        except Exception as e:
            logger.error(f"[Scheduler][EXCHANGE] error: {e}")

    # UR monthly refresh
    def job_ur_refresh():
        try:
            from database import SessionLocal
            db = SessionLocal()
            logger.info("[Scheduler] Running UR refresh job...")
            success, message, count = ur_excel_processor.refresh_data(db)
            logger.info(f"[Scheduler][UR] success={success} msg='{message}' count={count}")
            db.close()
        except Exception as e:
            logger.error(f"[Scheduler][UR] error: {e}")

    # Parse cron strings
    def _cron(trigger_expr: str):
        # expected format: "m h dom mon dow"
        parts = trigger_expr.split()
        if len(parts) != 5:
            raise ValueError(f"Invalid cron expression: {trigger_expr}")
        minute, hour, day, month, dow = parts
        return CronTrigger(minute=minute, hour=hour, day=day, month=month, day_of_week=dow, timezone=tz)

    _scheduler.add_job(job_ui_refresh, _cron(CRON_UI_REFRESH), id="ui_refresh", replace_existing=True)
    _scheduler.add_job(job_exchange_refresh, _cron(CRON_EXCHANGE_REFRESH), id="exchange_refresh", replace_existing=True)
    _scheduler.add_job(job_ur_refresh, _cron(CRON_UR_REFRESH), id="ur_refresh", replace_existing=True)
    logger.info("[Scheduler] Jobs scheduled: ui_refresh, exchange_refresh, ur_refresh")

# Excel processor instance
excel_processor = ExcelProcessor()
ur_excel_processor = URExcelProcessor()
exchange_rate_excel_processor = ExchangeRateExcelProcessor()
exchange_rate_bcu_processor = ExchangeRateBCUProcessor()
brou_processor = BROUProcessor()

# =============================================================================
# Simple in-memory job manager for long-running tasks (exchange historical refresh)
# =============================================================================
from threading import Lock

class JobStatus:
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"

class JobManager:
    def __init__(self):
        self._jobs: dict[str, dict] = {}
        self._lock = Lock()

    def create_job(self, job_type: str) -> str:
        job_id = str(uuid.uuid4())
        with self._lock:
            self._jobs[job_id] = {
                "job_id": job_id,
                "type": job_type,
                "status": JobStatus.PENDING,
                "message": None,
                "created_at": time.time(),
                "started_at": None,
                "finished_at": None,
                "duration": None,
                "result": None,
                "error": None,
            }
        return job_id

    def mark_running(self, job_id: str):
        with self._lock:
            job = self._jobs.get(job_id)
            if job and job["status"] == JobStatus.PENDING:
                job["status"] = JobStatus.RUNNING
                job["started_at"] = time.time()

    def mark_success(self, job_id: str, message: str, result: dict | None):
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job["status"] = JobStatus.SUCCESS
                job["message"] = message
                job["finished_at"] = time.time()
                if job.get("started_at"):
                    job["duration"] = job["finished_at"] - job["started_at"]
                job["result"] = result

    def mark_error(self, job_id: str, error: str):
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job["status"] = JobStatus.ERROR
                job["error"] = error
                job["message"] = error
                job["finished_at"] = time.time()
                if job.get("started_at"):
                    job["duration"] = job["finished_at"] - job["started_at"]

    def get(self, job_id: str) -> dict | None:
        with self._lock:
            job = self._jobs.get(job_id)
            # Return a shallow copy to avoid external mutation
            return dict(job) if job else None

    def find_running_job(self, job_type: str) -> str | None:
        with self._lock:
            for jid, meta in self._jobs.items():
                if meta["type"] == job_type and meta["status"] in (JobStatus.PENDING, JobStatus.RUNNING):
                    return jid
        return None

job_manager = JobManager()


# Mount static files only if they exist
if os.path.exists(STATIC_DIRECTORY):
    app.mount(STATIC_MOUNT_PATH, StaticFiles(directory=STATIC_DIRECTORY), name=STATIC_NAME)

@app.get(ENDPOINT_HEALTH, tags=["🏠 Sistema"])
async def health_check():
    """
    **Health Check del Sistema**
    
    Verifica que el servicio SIFU esté funcionando correctamente.
    
    - **Respuesta**: Estado del servicio y timestamp actual
    - **Uso**: Monitoreo y verificación de disponibilidad
    """
    return {FIELD_STATUS: MSG_HEALTH_OK, FIELD_TIMESTAMP: datetime.utcnow().isoformat()}

@app.get("/api/ui/latest", tags=["📈 Unidad Indexada (UI)"])
async def get_latest_ui(db: Session = Depends(get_db)):
    """
    **Obtener Último Valor de UI**
    
    Consulta el valor más reciente de la Unidad Indexada disponible en la base de datos.
    
    - **Fuente**: Instituto Nacional de Estadística (INE)
    - **Actualización**: Datos actualizados periódicamente desde INE
    - **Formato**: Valor decimal con fecha correspondiente
    
    **Ejemplo de uso**: Consultar el valor actual de UI para cálculos de reajuste.
    """
    try:
        service = UIService(db)
        latest_ui = service.get_latest_ui()
        
        if latest_ui:
            return UIResponse(
                success=True,
                message=MSG_LATEST_UI_SUCCESS,
                data=latest_ui.dict() if hasattr(latest_ui, 'dict') else latest_ui
            ).dict()
        else:
            return UIResponse(
                success=False,
                message=MSG_NO_UI_DATA
            ).dict()
    
    except Exception as e:
        logger.error(f"Error getting latest UI value: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/api/ui/{date}", tags=["📈 Unidad Indexada (UI)"])
async def get_ui_by_date(date: date, db: Session = Depends(get_db)):
    """
    **Obtener UI por Fecha Específica**
    
    Consulta el valor de la Unidad Indexada para una fecha determinada.
    
    - **Parámetro**: Fecha en formato YYYY-MM-DD
    - **Búsqueda inteligente**: Si no hay datos para la fecha exacta, devuelve el valor más cercano anterior
    - **Rango disponible**: Desde 2002 hasta la fecha actual
    
    **Ejemplo**: `/api/ui/2024-12-01` → Valor de UI del 1 de diciembre de 2024
    """
    try:
        service = UIService(db)
        ui_value = service.get_ui_by_date(date)
        
        if ui_value:
            return UIResponse(
                success=True,
                message=f"UI value for {date} retrieved successfully",
                data=ui_value.dict() if hasattr(ui_value, 'dict') else ui_value
            ).dict()
        else:
            # Try to find the closest value
            closest_ui = service.get_ui_closest_to_date(date)
            if closest_ui:
                return UIResponse(
                    success=True,
                    message=f"No data for {date}. Showing closest previous value",
                    data=closest_ui.dict() if hasattr(closest_ui, 'dict') else closest_ui
                ).dict()
            else:
                raise HTTPException(status_code=404, detail=f"No UI data found for {date} or previous dates")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting UI by date {date}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ui/range/{start_date}/{end_date}", tags=["📈 Unidad Indexada (UI)"])
async def get_ui_by_range(start_date: date, end_date: date, db: Session = Depends(get_db)):
    """
    **Obtener UI por Rango de Fechas**
    
    Consulta múltiples valores de UI dentro de un período específico.
    
    - **Parámetros**: Fecha inicio y fin en formato YYYY-MM-DD
    - **Validación**: Fecha inicio debe ser menor o igual a fecha fin
    - **Respuesta**: Array de valores con sus fechas correspondientes
    
    **Ejemplo**: `/api/ui/range/2024-01-01/2024-01-31` → Todos los valores de enero 2024
    """
    try:
        if start_date > end_date:
            raise HTTPException(
                status_code=400, 
                detail="Start date must be less than or equal to end date"
            )
        
        service = UIService(db)
        ui_values = service.get_ui_by_date_range(start_date, end_date)
        
        return UIResponse(
            success=True,
            message=f"UI values for range {start_date} - {end_date} retrieved successfully. {len(ui_values)} records found",
            data=[item.dict() if hasattr(item, 'dict') else item for item in ui_values]
        ).dict()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting UI by range {start_date} - {end_date}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/info", tags=["🏠 Sistema"])
async def get_info(db: Session = Depends(get_db)):
    """
    **Información General del Sistema UI**
    
    Obtiene estadísticas y metadatos sobre los datos de Unidad Indexada disponibles.
    
    - **Total registros**: Cantidad de valores UI almacenados
    - **Rango de fechas**: Primera y última fecha disponible
    - **Último valor**: Valor UI más reciente
    - **Fuente**: Información sobre el origen de los datos
    
    **Uso**: Verificar disponibilidad de datos antes de consultas específicas.
    """
    try:
        service = UIService(db)
        total_records = service.get_total_records()
        min_date, max_date = service.get_date_range_available()
        latest_ui = service.get_latest_ui()
        
        return {
            "total_records": total_records,
            "date_range": {
                "min_date": min_date.isoformat() if min_date else None,
                "max_date": max_date.isoformat() if max_date else None
            },
            "latest_ui": latest_ui.dict() if latest_ui else None,
            "data_source": "Instituto Nacional de Estadística - Uruguay"
        }
    
    except Exception as e:
        logger.error(f"Error getting information: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/refresh", tags=["📈 Unidad Indexada (UI)"])
async def refresh_data(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    **Actualizar Datos de UI desde INE**
    
    Descarga y procesa la última planilla de Unidad Indexada desde el sitio oficial del INE.
    
    - **Acción**: Descarga automática desde INE
    - **Procesamiento**: Valida y actualiza base de datos
    - **Respuesta**: Cantidad de registros procesados y fecha de última actualización
    - **Tiempo**: Puede tomar unos segundos debido a la descarga
    
    **⚠️ Nota**: Solo ejecutar cuando se necesiten datos actualizados del INE.
    """
    try:
        # Execute the update
        success, message, total_records = excel_processor.refresh_data(db)
        
        if success:
            # Get the most recent date after the update
            service = UIService(db)
            latest_ui = service.get_latest_ui()
            
            return RefreshResponse(
                success=True,
                message=message,
                total_records=total_records,
                last_updated=latest_ui.date if latest_ui else None
            ).dict()
        else:
            return RefreshResponse(
                success=False,
                message=message,
                total_records=0
            ).dict()
    
    except Exception as e:
        logger.error(f"Error updating data: {e}")
        return RefreshResponse(
            success=False,
            message=f"Internal error: {str(e)}",
            total_records=0
        )

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("🚀 Starting SIFU...")
    
    # Try to load initial data if it doesn't exist
    try:
        from database import SessionLocal
        db = SessionLocal()
        service = UIService(db)
        
        if service.get_total_records() == 0:
            logger.info("No data in database. Attempting to load initial data...")
            success, message, total_records = excel_processor.refresh_data(db)
            if success:
                logger.info(f"✅ Initial data loaded: {total_records} records")
            else:
                logger.warning(f"⚠️ Could not load initial data: {message}")
        else:
            logger.info(f"✅ Database ready with {service.get_total_records()} records")
        
        db.close()
    except Exception as e:
        logger.error(f"Error in startup: {e}")

    # Start background scheduler if enabled and available
    try:
        if SCHEDULER_ENABLED and AsyncIOScheduler and CronTrigger:
            global scheduler
            scheduler = AsyncIOScheduler()
            _add_jobs(scheduler)
            scheduler.start()
            logger.info(f"[Scheduler] Started (tz={SCHEDULER_TIMEZONE})")
        else:
            logger.info("[Scheduler] Disabled or APScheduler not installed")
    except Exception as e:
        logger.error(f"[Scheduler] Failed to start: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    # Gracefully stop scheduler
    global scheduler
    if scheduler:
        try:
            scheduler.shutdown(wait=False)
            logger.info("[Scheduler] Stopped")
        except Exception as e:
            logger.error(f"[Scheduler] Error on shutdown: {e}")

@app.get("/api/ur/latest", tags=["💰 Unidad Reajustable (UR)"])
async def get_latest_ur(db: Session = Depends(get_db)):
    """
    **Obtener Último Valor de UR**
    
    Consulta el valor más reciente de la Unidad Reajustable disponible.
    
    - **Fuente**: Banco Hipotecario del Uruguay (BHU)
    - **Frecuencia**: Datos mensuales desde 1969
    - **Formato**: Valor decimal con año y mes correspondiente
    
    **Uso principal**: Cálculo de reajustes en créditos hipotecarios y otros contratos.
    """
    try:
        ur_service = URService(db)
        latest_ur = ur_service.get_latest_ur()
        
        if latest_ur:
            return URResponse(
                success=True,
                message="Latest UR value retrieved successfully",
                data=latest_ur.dict() if hasattr(latest_ur, 'dict') else latest_ur
            ).dict()
        else:
            return URResponse(
                success=False,
                message="No UR data available",
                data=None
            ).dict()
            
    except Exception as e:
        logger.error(f"Error in get_latest_ur: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.get("/api/ur/year-month/{year}/{month}", tags=["💰 Unidad Reajustable (UR)"])
async def get_ur_by_year_month(year: int, month: int, db: Session = Depends(get_db)):
    """
    **Obtener UR por Año y Mes**
    
    Consulta el valor de UR para un mes específico de un año determinado.
    
    - **Parámetros**: Año (YYYY) y mes (1-12)
    - **Validación**: Mes debe estar entre 1 y 12
    - **Disponibilidad**: Desde enero 1969 hasta el mes actual
    
    **Ejemplo**: `/api/ur/year-month/2024/12` → UR de diciembre 2024
    """
    try:
        # Validate month
        if month < 1 or month > 12:
            return URResponse(
                success=False,
                message="Month must be between 1 and 12",
                data=None
            ).dict()
        
        ur_service = URService(db)
        ur_value = ur_service.get_ur_by_year_month(year, month)
        
        if ur_value:
            return URResponse(
                success=True,
                message=f"UR value for {year}-{month:02d} retrieved successfully",
                data=ur_value.dict() if hasattr(ur_value, 'dict') else ur_value
            ).dict()
        else:
            return URResponse(
                success=False,
                message=f"No UR data available for {year}-{month:02d}",
                data=None
            ).dict()
                
    except Exception as e:
        logger.error(f"Error in get_ur_by_year_month: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.get("/api/ur/year/{year}", tags=["💰 Unidad Reajustable (UR)"])
async def get_ur_by_year(year: int, db: Session = Depends(get_db)):
    """
    **Obtener Todos los UR de un Año**
    
    Consulta todos los valores mensuales de UR para un año completo.
    
    - **Parámetro**: Año (YYYY)
    - **Respuesta**: Array con hasta 12 valores (enero a diciembre)
    - **Útil para**: Análisis de evolución anual de UR
    
    **Ejemplo**: `/api/ur/year/2024` → Todos los UR del año 2024
    """
    try:
        ur_service = URService(db)
        ur_values = ur_service.get_ur_by_year(year)
        
        if ur_values:
            return URResponse(
                success=True,
                message=f"Retrieved {len(ur_values)} UR values for year {year}",
                data=[item.dict() if hasattr(item, 'dict') else item for item in ur_values]
            ).dict()
        else:
            return URResponse(
                success=False,
                message=f"No UR data available for year {year}",
                data=[]
            ).dict()
            
    except Exception as e:
        logger.error(f"Error in get_ur_by_year: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.get("/api/ur/range/{start_year}/{start_month}/{end_year}/{end_month}", tags=["💰 Unidad Reajustable (UR)"])
async def get_ur_by_range(start_year: int, start_month: int, end_year: int, end_month: int, db: Session = Depends(get_db)):
    """
    **Obtener UR por Rango de Períodos**
    
    Consulta valores de UR dentro de un rango de años y meses específico.
    
    - **Parámetros**: Año/mes inicio y año/mes fin
    - **Validaciones**: Meses entre 1-12, período inicio ≤ período fin
    - **Útil para**: Análisis históricos de evolución de UR
    
    **Ejemplo**: `/api/ur/range/2020/1/2024/12` → UR desde enero 2020 hasta diciembre 2024
    """
    try:
        # Validate months
        if start_month < 1 or start_month > 12 or end_month < 1 or end_month > 12:
            return URResponse(
                success=False,
                message="Months must be between 1 and 12",
                data=None
            ).dict()
        
        # Validate range
        if (start_year > end_year) or (start_year == end_year and start_month > end_month):
            return URResponse(
                success=False,
                message="Start period must be before or equal to end period",
                data=None
            ).dict()
        
        ur_service = URService(db)
        ur_values = ur_service.get_ur_by_range(start_year, start_month, end_year, end_month)
        
        if ur_values:
            return URResponse(
                success=True,
                message=f"Retrieved {len(ur_values)} UR values for range {start_year}-{start_month:02d} to {end_year}-{end_month:02d}",
                data=[item.dict() if hasattr(item, 'dict') else item for item in ur_values]
            ).dict()
        else:
            return URResponse(
                success=False,
                message=f"No UR data available for range {start_year}-{start_month:02d} to {end_year}-{end_month:02d}",
                data=[]
            ).dict()
            
    except Exception as e:
        logger.error(f"Error in get_ur_by_range: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.post("/api/ur/range", tags=["💰 Unidad Reajustable (UR)"])
async def get_ur_by_range_post(request: dict, db: Session = Depends(get_db)):
    """
    **Obtener UR por Rango (POST)**
    
    Versión POST del endpoint de rango para consultas complejas con body JSON.
    
    - **Body**: `{"start_year": 2020, "start_month": 1, "end_year": 2024, "end_month": 12}`
    - **Funcionalidad**: Idéntica al endpoint GET equivalente
    """
    start_year = request.get('start_year')
    start_month = request.get('start_month', 1)
    end_year = request.get('end_year')
    end_month = request.get('end_month', 12)
    return await get_ur_by_range(start_year, start_month, end_year, end_month, db)

@app.post("/api/ur/refresh", tags=["💰 Unidad Reajustable (UR)"])
async def refresh_ur_data(db: Session = Depends(get_db)):
    """
    **Actualizar Datos de UR desde BHU**
    
    Descarga y procesa la última planilla de UR desde el sitio oficial del BHU.
    
    - **Fuente**: Banco Hipotecario del Uruguay
    - **Proceso**: Descarga Excel, extrae valores mensuales y actualiza base de datos
    - **Datos**: Histórico completo desde 1969
    - **Tiempo**: Puede tomar unos segundos debido a la descarga
    
    **⚠️ Nota**: Solo ejecutar cuando se necesiten datos actualizados del BHU.
    """
    try:
        logger.info("Starting UR data update...")
        
        success, message, count = ur_excel_processor.refresh_data(db)
        
        # Get additional information
        ur_service = URService(db)
        total_records = ur_service.get_total_records()
        latest_ur = ur_service.get_latest_ur()
        
        return RefreshResponse(
            success=success,
            message=message,
            total_records=total_records,
            last_updated=None  # UR has no specific date, only year-month
        ).dict()
        
    except Exception as e:
        logger.error(f"Error in refresh_ur_data: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.get("/api/ur/info", tags=["💰 Unidad Reajustable (UR)"])
async def get_ur_info(db: Session = Depends(get_db)):
    """
    **Información del Sistema UR**
    
    Obtiene estadísticas y metadatos sobre los datos de UR disponibles.
    
    - **Total registros**: Cantidad de valores UR almacenados
    - **Rango de años**: Primer y último año disponible (desde 1969)
    - **Último valor**: Valor UR más reciente
    - **Años disponibles**: Lista completa de años con datos
    
    **Uso**: Verificar disponibilidad de datos antes de consultas específicas.
    """
    try:
        ur_service = URService(db)
        
        total_records = ur_service.get_total_records()
        min_year, max_year = ur_service.get_year_range_available()
        latest_ur = ur_service.get_latest_ur()
        available_years = ur_service.get_available_years()
        
        return {
            "success": True,
            "data": {
                "total_records": total_records,
                "year_range": {
                    "min_year": min_year,
                    "max_year": max_year
                },
                "latest_value": latest_ur.dict() if latest_ur else None,
                "available_years": available_years
            }
        }
        
    except Exception as e:
        logger.error(f"Error in get_ur_info: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )



# =============================================================================
# EXCHANGE RATE ENDPOINTS
# =============================================================================

@app.get(ENDPOINT_EXCHANGE_RATE_LATEST, tags=["💱 Cotizaciones de Monedas"])
async def get_latest_exchange_rates(currencies: Optional[str] = None, db: Session = Depends(get_db)):
    """
    **Obtener Últimas Cotizaciones Históricas**
    
    Consulta las cotizaciones más recientes disponibles en los datos históricos del INE.
    
    - **Parámetro opcional**: Lista de monedas separadas por comas (USD,EUR,ARS,BRL)
    - **Fuente**: Instituto Nacional de Estadística (datos históricos)
    - **Cobertura**: 23+ años de datos (desde 2001)
    
    **Nota**: Para cotizaciones actuales usar `/api/exchange-rate/current` (BCU)
    """
    try:
        service = ExchangeRateService(db)
        currency_list = currencies.split(',') if currencies else None
        
        exchange_rates = service.get_latest_exchange_rates(currency_list)
        
        if exchange_rates:
            return ExchangeRateResponse(
                success=True,
                message=MSG_LATEST_EXCHANGE_RATE_SUCCESS,
                data=[rate.dict() for rate in exchange_rates]
            ).dict()
        else:
            return ExchangeRateResponse(
                success=False,
                message=MSG_NO_EXCHANGE_RATE_DATA
            ).dict()
    
    except Exception as e:
        logger.error(f"Error getting latest exchange rates: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get(ENDPOINT_EXCHANGE_RATE_INFO, tags=["💱 Cotizaciones de Monedas"])
async def get_exchange_rate_info(db: Session = Depends(get_db)):
    """
    **Información del Sistema de Cotizaciones**
    
    Obtiene estadísticas sobre los datos históricos de cotizaciones disponibles.
    
    - **Total registros**: 23,000+ cotizaciones históricas (INE)
    - **Rango de fechas**: Desde 2001 hasta presente
    - **Monedas disponibles**: USD, EUR, ARS, BRL (datos históricos)
    - **Últimas cotizaciones**: Valores más recientes por moneda
    
    **Sistemas disponibles**: Histórico (INE) + Tiempo Real (BCU en `/current`)
    """
    try:
        service = ExchangeRateService(db)
        total_records = service.get_total_records()
        min_date, max_date = service.get_date_range_available()
        available_currencies = service.get_available_currencies()
        latest_rates = service.get_latest_exchange_rates()
        
        return {
            "total_records": total_records,
            "date_range": {
                "min_date": min_date.isoformat() if min_date else None,
                "max_date": max_date.isoformat() if max_date else None
            },
            "available_currencies": available_currencies,
            "latest_rates": [rate.dict() for rate in latest_rates],
            "data_source": "Banco Central del Uruguay"
        }
    
    except Exception as e:
        logger.error(f"Error getting exchange rate information: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get(ENDPOINT_EXCHANGE_RATE_BY_CURRENCY, tags=["💱 Cotizaciones de Monedas"])
async def get_exchange_rates_by_currency(currency: str, limit: int = 30, db: Session = Depends(get_db)):
    """
    **Obtener Historial de una Moneda Específica**
    
    Consulta los valores históricos más recientes de una moneda determinada.
    
    - **Parámetro**: Código de moneda (USD, EUR, ARS, BRL)
    - **Límite**: Número máximo de registros (default: 30)
    - **Orden**: Del más reciente al más antiguo
    
    **Ejemplo**: `/api/exchange-rate/currency/USD?limit=10` → Últimas 10 cotizaciones del dólar
    """
    try:
        if currency.upper() not in VALID_CURRENCY_CODES:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"Invalid currency code. Supported currencies: {', '.join(VALID_CURRENCY_CODES)}"
            )
        
        service = ExchangeRateService(db)
        exchange_rates = service.get_exchange_rate_by_currency(currency, limit)
        
        if exchange_rates:
            return ExchangeRateResponse(
                success=True,
                message=MSG_EXCHANGE_RATE_CURRENCY_SUCCESS.format(currency=currency.upper()),
                data=[rate.dict() for rate in exchange_rates]
            ).dict()
        else:
            return ExchangeRateResponse(
                success=False,
                message=MSG_NO_EXCHANGE_RATE_CURRENCY_DATA.format(currency=currency.upper())
            ).dict()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting exchange rates by currency {currency}: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get(ENDPOINT_EXCHANGE_RATE_RANGE, tags=["💱 Cotizaciones de Monedas"])
async def get_exchange_rates_by_range(start_date: date, end_date: date, currency: Optional[str] = None, db: Session = Depends(get_db)):
    """
    **Obtener Cotizaciones por Rango de Fechas**
    
    Consulta cotizaciones históricas dentro de un período específico.
    
    - **Parámetros**: Fecha inicio y fin (YYYY-MM-DD)
    - **Filtro opcional**: Moneda específica
    - **Validación**: Fecha inicio ≤ fecha fin
    
    **Ejemplo**: `/api/exchange-rate/range/2024-01-01/2024-01-31?currency=USD` → USD de enero 2024
    """
    try:
        if start_date > end_date:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=MSG_INVALID_DATE_RANGE
            )
        
        if currency and currency.upper() not in VALID_CURRENCY_CODES:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"Invalid currency code. Supported currencies: {', '.join(VALID_CURRENCY_CODES)}"
            )
        
        service = ExchangeRateService(db)
        exchange_rates = service.get_exchange_rate_by_date_range(start_date, end_date, currency)
        
        return ExchangeRateResponse(
            success=True,
            message=MSG_EXCHANGE_RATE_RANGE_SUCCESS.format(
                start_date=start_date, 
                end_date=end_date, 
                count=len(exchange_rates)
            ),
            data=[rate.dict() for rate in exchange_rates]
        ).dict()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting exchange rates by range {start_date} - {end_date}: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post(ENDPOINT_EXCHANGE_RATE_REFRESH, tags=["💱 Cotizaciones de Monedas"])
async def refresh_exchange_rate_historical_data(db: Session = Depends(get_db)):
    """
    **Actualizar Datos Históricos de Cotizaciones**
    
    Descarga y procesa la planilla histórica de cotizaciones desde el INE.
    
    - **Fuente**: Instituto Nacional de Estadística
    - **Datos**: 23+ años de cotizaciones históricas (2001-presente)
    - **Proceso**: Descarga Excel, extrae cotizaciones y actualiza base de datos
    - **Tiempo**: Puede tomar tiempo debido al tamaño del archivo
    
    **⚠️ Nota**: Para datos actuales usar `/current` (BCU). Este endpoint es para históricos.
    """
    try:
        logger.info("Starting historical exchange rate data update from INE (synchronous endpoint)...")
        success, message, total_records = exchange_rate_excel_processor.refresh_data(db)
        if success:
            service = ExchangeRateService(db)
            total_db_records = service.get_total_records()
            min_date, max_date = service.get_date_range_available()
            return ExchangeRateResponse(
                success=True,
                message=message,
                data={
                    "total_records": total_records,
                    "total_db_records": total_db_records,
                    "date_range": {
                        "min_date": min_date.isoformat() if min_date else None,
                        "max_date": max_date.isoformat() if max_date else None
                    }
                }
            ).dict()
        return ExchangeRateResponse(success=False, message=message, data=None).dict()
    except Exception as e:
        logger.error(f"Error refreshing historical exchange rate data: {e}")
        return ExchangeRateResponse(success=False, message=f"Internal error: {str(e)}", data=None).dict()


# -----------------------------------------------------------------------------
# ASYNC JOB VERSION (202 Accepted + polling)
# -----------------------------------------------------------------------------
ASYNC_JOB_TYPE_EXCHANGE_REFRESH = "exchange_rate_refresh"

def _run_exchange_refresh_job(job_id: str):  # runs in background thread
    """Internal function executed in background to perform the heavy refresh and update job metadata."""
    job_manager.mark_running(job_id)
    # New DB session (cannot reuse dependency outside request context)
    from database import SessionLocal
    db_local = SessionLocal()
    try:
        logger.info(f"[Job {job_id}] Running exchange historical refresh")
        success, message, total_records = exchange_rate_excel_processor.refresh_data(db_local)
        if success:
            service = ExchangeRateService(db_local)
            total_db_records = service.get_total_records()
            min_date, max_date = service.get_date_range_available()
            result_summary = {
                "total_records": total_records,
                "total_db_records": total_db_records,
                "date_range": {
                    "min_date": min_date.isoformat() if min_date else None,
                    "max_date": max_date.isoformat() if max_date else None
                }
            }
            job_manager.mark_success(job_id, message, result_summary)
            logger.info(f"[Job {job_id}] Completed successfully")
        else:
            job_manager.mark_error(job_id, message or "Unknown failure")
            logger.warning(f"[Job {job_id}] Failed: {message}")
    except Exception as e:  # noqa: BLE001
        logger.error(f"[Job {job_id}] Exception: {e}")
        job_manager.mark_error(job_id, f"Exception: {e}")
    finally:
        db_local.close()


@app.post("/api/exchange-rate/refresh-async", status_code=202, tags=["💱 Cotizaciones de Monedas"], summary="Iniciar actualización histórica (asíncrona)")
async def start_exchange_rate_refresh_async(background_tasks: BackgroundTasks):
    """Inicia la actualización histórica de cotizaciones en background.

    Respuesta inmediata (202 Accepted) con un job_id para consultar estado.
    Si ya existe un job en curso para este tipo, se devuelve ese job en lugar de crear otro.
    """
    # Avoid parallel duplicate jobs
    existing = job_manager.find_running_job(ASYNC_JOB_TYPE_EXCHANGE_REFRESH)
    if existing:
        job = job_manager.get(existing)
        return JSONResponse(status_code=202, content={
            "job_id": existing,
            "status": job["status"],
            "message": "Job already running",
            "type": job["type"],
        })

    job_id = job_manager.create_job(ASYNC_JOB_TYPE_EXCHANGE_REFRESH)
    background_tasks.add_task(_run_exchange_refresh_job, job_id)
    return {"job_id": job_id, "status": JobStatus.PENDING, "message": "Job accepted", "type": ASYNC_JOB_TYPE_EXCHANGE_REFRESH}


@app.get("/api/jobs/{job_id}", tags=["💱 Cotizaciones de Monedas"], summary="Estado de un job")
async def get_job_status(job_id: str):
    job = job_manager.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    # Provide ISO timestamps if present
    def _ts(ts):
        return None if ts is None else datetime.utcfromtimestamp(ts).isoformat() + "Z"
    job_out = dict(job)
    for fld in ("created_at", "started_at", "finished_at"):
        job_out[fld] = _ts(job_out[fld])
    return job_out


@app.get("/api/jobs", tags=["💱 Cotizaciones de Monedas"], summary="Listado de jobs (debug)")
async def list_jobs():
    # WARNING: In-memory only; suitable for development/testing
    ids = []
    # Access internal structure safely
    for job_id in list(job_manager._jobs.keys()):  # type: ignore[attr-defined]
        job = job_manager.get(job_id)
        if job:
            ids.append({"job_id": job_id, "type": job["type"], "status": job["status"]})
    return {"jobs": ids}


@app.get("/api/exchange-rate/refresh-status/{job_id}", tags=["💱 Cotizaciones de Monedas"], summary="Alias estado refresh histórico")
async def get_exchange_refresh_status(job_id: str):
    return await get_job_status(job_id)


@app.get("/api/exchange-rate/current", tags=["💱 Cotizaciones de Monedas"])
async def get_current_exchange_rates():
    """
    **🔥 Obtener Cotizaciones Actuales (BCU - Tiempo Real)**
    
    Consulta las cotizaciones actuales del Banco Central del Uruguay.
    
    - **Fuente**: BCU (scraping web en tiempo real)
    - **Monedas**: USD, EUR, ARS, BRL
    - **Actualización**: Datos actuales del BCU
    - **Formato**: Compra, venta y promedio por moneda
    
    **⭐ Recomendado**: Para cotizaciones actuales. Para históricos usar otros endpoints.
    """
    try:
        logger.info("Getting current exchange rates from BCU...")
        
        # Get current rates from BCU
        current_rates, is_from_bcu = exchange_rate_bcu_processor.get_current_rates()
        
        if current_rates:
            formatted_rates = []
            source = "BCU" if is_from_bcu else "Historical Data"
            for currency, buy, sell, avg in current_rates:
                formatted_rates.append({
                    "currency": currency,
                    "buy_rate": buy,
                    "sell_rate": sell,
                    "average_rate": avg,
                    "source": source,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            return ExchangeRateResponse(
                success=True,
                message=f"Current exchange rates retrieved successfully. {len(current_rates)} currencies",
                data=formatted_rates
            ).dict()
        else:
            return ExchangeRateResponse(
                success=False,
                message="Could not retrieve current exchange rates from BCU",
                data=None
            ).dict()
    
    except Exception as e:
        logger.error(f"Error getting current exchange rates: {e}")
        return ExchangeRateResponse(
            success=False,
            message=f"Internal error: {str(e)}",
            data=None
        ).dict()

@app.get(ENDPOINT_EXCHANGE_RATE_BY_DATE, tags=["💱 Cotizaciones de Monedas"])
async def get_exchange_rates_by_date(date: date, currency: Optional[str] = None, db: Session = Depends(get_db)):
    """
    **Obtener Cotizaciones por Fecha Específica**
    
    Consulta las cotizaciones históricas para una fecha determinada.
    
    - **Parámetro**: Fecha (YYYY-MM-DD)
    - **Filtro opcional**: Moneda específica
    - **Búsqueda inteligente**: Si no hay datos exactos, busca fecha más cercana
    
    **Ejemplo**: `/api/exchange-rate/2024-12-01?currency=USD` → USD del 1 dic 2024
    """
    try:
        service = ExchangeRateService(db)
        exchange_rates = service.get_exchange_rate_by_date(date, currency)
        
        if exchange_rates:
            return ExchangeRateResponse(
                success=True,
                message=MSG_EXCHANGE_RATE_DATE_SUCCESS.format(date=date),
                data=[rate.dict() for rate in exchange_rates]
            ).dict()
        else:
            return ExchangeRateResponse(
                success=False,
                message=MSG_NO_EXCHANGE_RATE_DATE_DATA.format(date=date)
            ).dict()
    
    except Exception as e:
        logger.error(f"Error getting exchange rates by date {date}: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get(ENDPOINT_EXCHANGE_RATE_BY_DATE_CURRENCY, tags=["💱 Cotizaciones de Monedas"])
async def get_exchange_rate_by_date_and_currency(date: date, currency: str, db: Session = Depends(get_db)):
    """
    **Obtener Cotización Específica (Fecha + Moneda)**
    
    Consulta el valor exacto de una moneda en una fecha determinada.
    
    - **Parámetros**: Fecha (YYYY-MM-DD) + código de moneda
    - **Respuesta**: Un solo registro con compra, venta y promedio
    - **Error 404**: Si no hay datos para esa combinación
    
    **Ejemplo**: `/api/exchange-rate/2024-12-01/USD` → USD específico del 1 dic 2024
    """
    try:
        if currency.upper() not in VALID_CURRENCY_CODES:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"Invalid currency code. Supported currencies: {', '.join(VALID_CURRENCY_CODES)}"
            )
        
        service = ExchangeRateService(db)
        exchange_rate = service.get_exchange_rate_closest_to_date(date, currency)
        
        if exchange_rate:
            return ExchangeRateResponse(
                success=True,
                message=f"Exchange rate for {currency.upper()} on {date} retrieved successfully",
                data=exchange_rate.dict()
            ).dict()
        else:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f"No exchange rate data found for {currency.upper()} on {date} or previous dates"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting exchange rate by date {date} and currency {currency}: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/api/brou/current", tags=["🏦 BROU"])
async def get_current_brou_rates():
    """
    **🏦 Obtener Cotizaciones Actuales del BROU**
    
    Consulta las cotizaciones actuales del Banco de la República Oriental del Uruguay.
    
    - **Fuente**: BROU (scraping web en tiempo real)
    - **Monedas**: USD, USD eBROU, EUR, ARS, BRL
    - **Datos**: Compra, venta, promedio y arbitrajes
    - **Arbitrajes**: EUR, ARS, BRL calculados vs USD
    - **Actualización**: Datos actuales del BROU
    
    **💡 Características especiales**:
    - USD eBROU: Cotización preferencial para clientes eBROU
    - Arbitrajes: Relación de cada moneda respecto al USD
    - Spreads reales: Diferencia entre compra y venta
    """
    try:
        logger.info("Getting current exchange rates from BROU...")
        
        # Get current rates from BROU
        current_rates, is_from_brou = brou_processor.get_current_rates()
        
        if current_rates:
            source = "BROU" if is_from_brou else "BROU_SAMPLE"
            
            return {
                "success": True,
                "message": f"Cotizaciones BROU obtenidas exitosamente. {len(current_rates)} monedas",
                "data": current_rates,
                "source": source,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "success": False,
                "message": "No se pudieron obtener las cotizaciones del BROU",
                "data": None
            }
    
    except Exception as e:
        logger.error(f"Error getting current BROU rates: {e}")
        return {
            "success": False,
            "message": f"Error interno: {str(e)}",
            "data": None
    }