#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import date, datetime
import asyncio
from typing import Optional
import logging
import uuid
import time
import os
from threading import Lock as ThreadLock
from bootstrap import perform_bootstrap

from database import get_db
from models import UIResponse, RefreshResponse, URResponse, ExchangeRateResponse
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

# Lifespan context replacing deprecated on_event startup/shutdown
async def _execute_startup():
    """Reusable startup logic; safe to call multiple times in tests."""
    logger.info("Starting SIFU (bootstrap + cache warmup)...")
    global scheduler
    # Legacy quick UI bootstrap
    try:
        db = None
        from database import SessionLocal as _SL  # local import for timing
        db = _SL()
        service = UIService(db)
        if service.get_total_records() == 0:
            try:
                excel_processor.refresh_data(db)
            except Exception as e:  # noqa: BLE001
                logger.error(f"[LegacyBootstrap] UI refresh failed: {e}")
    except Exception as e:  # noqa: BLE001
        logger.error(f"[LegacyBootstrap] skipped due to error: {e}")
    finally:
        if db:
            db.close()

    summary = perform_bootstrap(
        force=False,
        excel_processor=excel_processor,
        ur_excel_processor=ur_excel_processor,
        exchange_rate_excel_processor=exchange_rate_excel_processor,
    )
    logger.info(f"[Bootstrap] summary={summary}")

    # Warm caches
    try:
        _update_bcu_cache()
        _update_brou_cache()
    except Exception as e:  # noqa: BLE001
        logger.error(f"Cache warmup failed: {e}")

    # Launch hourly refresher once
    if not hasattr(_execute_startup, "_refresher_started"):
        async def cache_refresher_loop():
            while True:
                await asyncio.sleep(3600)
                logger.info("[CacheRefresher] Hourly refresh executing...")
                try:
                    _update_bcu_cache()
                    _update_brou_cache()
                except Exception as e:  # noqa: BLE001
                    logger.error(f"[CacheRefresher] failure: {e}")
        asyncio.create_task(cache_refresher_loop())
        _execute_startup._refresher_started = True  # type: ignore

    # Start scheduler once
    if scheduler is None:
        try:
            if SCHEDULER_ENABLED and AsyncIOScheduler and CronTrigger:
                scheduler = AsyncIOScheduler()
                _add_jobs(scheduler)
                scheduler.start()
                logger.info(f"[Scheduler] Started (tz={SCHEDULER_TIMEZONE})")
            else:
                logger.info("[Scheduler] Disabled or APScheduler not installed")
        except Exception as e:  # noqa: BLE001
            logger.error(f"[Scheduler] Failed to start: {e}")

    logger.info("Startup bootstrap complete")


# Legacy-compatible symbol for tests
async def startup_event():  # pragma: no cover
    await _execute_startup()


@asynccontextmanager
async def app_lifespan(app: FastAPI):  # type: ignore
    await _execute_startup()
    try:
        yield
    finally:
        global scheduler
        if scheduler:
            try:
                scheduler.shutdown(wait=False)
                logger.info("[Scheduler] Stopped")
            except Exception as e:  # noqa: BLE001
                logger.error(f"[Scheduler] Error on shutdown: {e}")


# Create FastAPI application with improved documentation and lifespan
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url=API_DOCS_URL,
    redoc_url=API_REDOC_URL,
    tags_metadata=[
        {
            "name": "Sistema",
            "description": "Endpoints de sistema: health check e informacion general"
        },
        {
            "name": TAG_UI,
            "description": (
                "Consulta de valores de la Unidad Indexada del Instituto Nacional de Estadistica (INE). "
                "La UI es un indice de ajuste por inflacion utilizado en Uruguay desde 2002."
            )
        },
        {
            "name": TAG_UR,
            "description": (
                "Consulta de valores de la Unidad Reajustable del Banco Hipotecario del Uruguay (BHU). "
                "La UR es un indice utilizado para reajustar creditos hipotecarios desde 1969."
            )
        },
        {
            "name": TAG_EXCHANGE,
            "description": (
                "Sistema dual de cotizaciones: datos historicos del INE (2001-presente) y "
                "cotizaciones actuales del BCU en tiempo real. Incluye USD, EUR, ARS, BRL."
            )
        },
        {
            "name": "BROU",
            "description": (
                "Cotizaciones del Banco de la Republica Oriental del Uruguay (BROU). "
                "Incluye USD, USD eBROU, EUR, ARS, BRL con valores de compra/venta y arbitrajes."
            )
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

@app.get("/", tags=["Sistema"])
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

# In-memory caches for current BCU & BROU rates (hourly refresh)
bcu_cache: dict | None = None
brou_cache: dict | None = None
_cache_lock = ThreadLock()

def _update_bcu_cache():
    global bcu_cache
    try:
        current_rates, is_from_bcu = exchange_rate_bcu_processor.get_current_rates()
        if not current_rates:
            logger.warning("[BCU Cache] No data fetched")
            return
        formatted = []
        source = "BCU" if is_from_bcu else "Historical Data"
        for currency, buy, sell, avg in current_rates:
            formatted.append({
                "currency": currency,
                "buy_rate": buy,
                "sell_rate": sell,
                "average_rate": avg,
                "source": source,
                "timestamp": datetime.utcnow().isoformat()
            })
        with _cache_lock:
            bcu_cache = {"data": formatted, "updated_at": datetime.utcnow()}
        logger.info(f"[BCU Cache] Updated ({len(formatted)} currencies)")
    except Exception as e:
        logger.error(f"[BCU Cache] Update failed: {e}")

def _update_brou_cache():
    global brou_cache
    try:
        current_rates, is_from_brou = brou_processor.get_current_rates()
        if not current_rates:
            logger.warning("[BROU Cache] No data fetched")
            return
        source = "BROU" if is_from_brou else "BROU_SAMPLE"
        formatted: list[dict] = []
        for rate in current_rates:
            # rate es un dict según BROUProcessor._get_sample_rates / get_current_rates
            try:
                currency = rate.get("currency")
                if not currency:
                    continue
                formatted.append({
                    "currency": currency,
                    "buy_rate": rate.get("buy_rate"),
                    "sell_rate": rate.get("sell_rate"),
                    "average_rate": rate.get("average_rate"),
                    "arbitrage_buy": rate.get("arbitrage_buy"),
                    "arbitrage_sell": rate.get("arbitrage_sell"),
                    # Preferencial: marcar USD_EBROU
                    "preferential": True if currency == "USD_EBROU" else None,
                    "source": source,
                    "timestamp": rate.get("timestamp") or datetime.utcnow().isoformat()
                })
            except Exception as e:  # noqa: BLE001
                logger.error(f"[BROU Cache] Skipping rate due to error: {e}")
        if not formatted:
            logger.warning("[BROU Cache] No valid rate entries after formatting. Using sample fallback.")
            try:
                sample_rates = brou_processor._get_sample_rates()  # noqa: SLF001 (internal fallback)
                for rate in sample_rates:
                    currency = rate.get("currency")
                    if not currency:
                        continue
                    formatted.append({
                        "currency": currency,
                        "buy_rate": rate.get("buy_rate"),
                        "sell_rate": rate.get("sell_rate"),
                        "average_rate": rate.get("average_rate"),
                        "arbitrage_buy": rate.get("arbitrage_buy"),
                        "arbitrage_sell": rate.get("arbitrage_sell"),
                        "preferential": True if currency == "USD_EBROU" else None,
                        "source": "BROU_SAMPLE",
                        "timestamp": rate.get("timestamp") or datetime.utcnow().isoformat()
                    })
            except Exception as fe:  # noqa: BLE001
                logger.error(f"[BROU Cache] Fallback sample failed: {fe}")
                return
        with _cache_lock:
            brou_cache = {"data": formatted, "updated_at": datetime.utcnow()}
        logger.info(f"[BROU Cache] Updated ({len(formatted)} currencies)")
    except Exception as e:
        logger.error(f"[BROU Cache] Update failed: {e}")

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

@app.get(ENDPOINT_HEALTH, tags=["Sistema"])
async def health_check():
    """Health check del sistema.

    Verifica que el servicio esta funcionando correctamente.
    """
    return {FIELD_STATUS: MSG_HEALTH_OK, FIELD_TIMESTAMP: datetime.utcnow().isoformat()}

@app.get("/api/ui/latest", tags=[TAG_UI])
async def get_latest_ui(db: Session = Depends(get_db)):
    """Obtener ultimo valor de UI (Unidad Indexada).

    Retorna el valor mas reciente disponible.
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

@app.get("/api/ui/{date}", tags=[TAG_UI])
async def get_ui_by_date(date: date, db: Session = Depends(get_db)):
    """Obtener UI por fecha especifica.

    Si no existe valor exacto se devuelve el mas cercano anterior.
    """
    try:
        service = UIService(db)
        ui_value = service.get_ui_by_date(date)
        
        if ui_value:
            return UIResponse(
                success=True,
                message=MSG_UI_DATE_SUCCESS.format(date=date),
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

@app.get("/api/ui/range/{start_date}/{end_date}", tags=[TAG_UI])
async def get_ui_by_range(start_date: date, end_date: date, db: Session = Depends(get_db)):
    """Obtener UI por rango de fechas (YYYY-MM-DD).

    Valida que start_date <= end_date.
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
            message=MSG_UI_RANGE_SUCCESS.format(start_date=start_date, end_date=end_date, count=len(ui_values)),
            data=[item.dict() if hasattr(item, 'dict') else item for item in ui_values]
        ).dict()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting UI by range {start_date} - {end_date}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/info", tags=["Sistema"])
async def get_info(db: Session = Depends(get_db)):
    """Informacion general del sistema UI (estadisticas basicas)."""
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
            "data_source": "National Institute of Statistics (INE) - Uruguay"
        }
    
    except Exception as e:
        logger.error(f"Error getting information: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/refresh", tags=[TAG_UI])
async def refresh_data(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Actualizar datos de UI desde INE (descarga y procesamiento)."""
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

    lifespan=app_lifespan,

@app.get("/api/ur/latest", tags=[TAG_UR])
async def get_latest_ur(db: Session = Depends(get_db)):
    """Obtener ultimo valor de UR (Unidad Reajustable)."""
    try:
        ur_service = URService(db)
        latest_ur = ur_service.get_latest_ur()
        
        if latest_ur:
            return URResponse(
                success=True,
                message=MSG_LATEST_UR_SUCCESS,
                data=latest_ur.dict() if hasattr(latest_ur, 'dict') else latest_ur
            ).dict()
        else:
            return URResponse(
                success=False,
                message= MSG_NO_UR_DATA,
                data=None
            ).dict()
            
    except Exception as e:
        logger.error(f"Error in get_latest_ur: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.get("/api/ur/year-month/{year}/{month}", tags=[TAG_UR])
async def get_ur_by_year_month(year: int, month: int, db: Session = Depends(get_db)):
    """Obtener UR por anio y mes (YYYY, 1-12)."""
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
                message=MSG_UR_YEAR_MONTH_SUCCESS.format(year=year, month=month),
                data=ur_value.dict() if hasattr(ur_value, 'dict') else ur_value
            ).dict()
        else:
            return URResponse(
                success=False,
                message=MSG_NO_UR_YEAR_MONTH_DATA.format(year=year, month=month),
                data=None
            ).dict()
                
    except Exception as e:
        logger.error(f"Error in get_ur_by_year_month: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.get("/api/ur/year/{year}", tags=[TAG_UR])
async def get_ur_by_year(year: int, db: Session = Depends(get_db)):
    """Obtener todos los valores UR de un anio."""
    try:
        ur_service = URService(db)
        ur_values = ur_service.get_ur_by_year(year)
        
        if ur_values:
            return URResponse(
                success=True,
                message=MSG_UR_YEAR_SUCCESS.format(count=len(ur_values), year=year),
                data=[item.dict() if hasattr(item, 'dict') else item for item in ur_values]
            ).dict()
        else:
            return URResponse(
                success=False,
                message=MSG_NO_UR_YEAR_DATA.format(year=year),
                data=[]
            ).dict()
            
    except Exception as e:
        logger.error(f"Error in get_ur_by_year: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.get("/api/ur/range/{start_year}/{start_month}/{end_year}/{end_month}", tags=[TAG_UR])
async def get_ur_by_range(start_year: int, start_month: int, end_year: int, end_month: int, db: Session = Depends(get_db)):
    """Obtener UR por rango de periodos (anio/mes inicio a anio/mes fin)."""
    try:
        # Validate months
        if start_month < 1 or start_month > 12 or end_month < 1 or end_month > 12:
            return URResponse(
                success=False,
                message=MSG_INVALID_MONTH if 'MSG_INVALID_MONTH' in globals() else "Months must be between 1 and 12",
                data=None
            ).dict()
        
        # Validate range
        if (start_year > end_year) or (start_year == end_year and start_month > end_month):
            return URResponse(
                success=False,
                message=MSG_INVALID_PERIOD_RANGE,
                data=None
            ).dict()
        
        ur_service = URService(db)
        ur_values = ur_service.get_ur_by_range(start_year, start_month, end_year, end_month)
        
        if ur_values:
            return URResponse(
                success=True,
                message=MSG_UR_RANGE_SUCCESS.format(count=len(ur_values), start_year=start_year, start_month=start_month, end_year=end_year, end_month=end_month),
                data=[item.dict() if hasattr(item, 'dict') else item for item in ur_values]
            ).dict()
        else:
            return URResponse(
                success=False,
                message=MSG_NO_UR_RANGE_DATA.format(start_year=start_year, start_month=start_month, end_year=end_year, end_month=end_month),
                data=[]
            ).dict()
            
    except Exception as e:
        logger.error(f"Error in get_ur_by_range: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.post("/api/ur/range", tags=[TAG_UR])
async def get_ur_by_range_post(request: dict, db: Session = Depends(get_db)):
    """Obtener UR por rango (POST). Body igual al endpoint GET correspondiente."""
    # Accept English or legacy Spanish keys
    start_year = request.get('start_year') or request.get('año_inicio') or request.get('ano_inicio')
    start_month = request.get('start_month') or request.get('mes_inicio') or 1
    end_year = request.get('end_year') or request.get('año_fin') or request.get('ano_fin') or start_year
    end_month = request.get('end_month') or request.get('mes_fin') or 12

    # Basic validation (mirrors GET endpoint logic)
    if None in (start_year, start_month, end_year, end_month):
        return URResponse(success=False, message="Missing required parameters").dict()
    try:
        start_year = int(start_year)
        start_month = int(start_month)
        end_year = int(end_year)
        end_month = int(end_month)
    except ValueError:
        return URResponse(success=False, message="Parameters must be integers").dict()
    if not (1 <= start_month <= 12 and 1 <= end_month <= 12):
        return URResponse(success=False, message="Months must be between 1 and 12").dict()
    if (end_year, end_month) < (start_year, start_month):
        return URResponse(success=False, message="Start period must be before or equal to end period").dict()
    return await get_ur_by_range(start_year, start_month, end_year, end_month, db)

@app.post("/api/ur/refresh", tags=[TAG_UR])
async def refresh_ur_data(db: Session = Depends(get_db)):
    """Actualizar datos de UR desde BHU (descarga + procesamiento)."""
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

@app.get("/api/ur/info", tags=[TAG_UR])
async def get_ur_info(db: Session = Depends(get_db)):
    """Informacion del sistema UR (estadisticas basicas)."""
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

@app.get(ENDPOINT_EXCHANGE_RATE_LATEST, tags=[TAG_EXCHANGE])
async def get_latest_exchange_rates(currencies: Optional[str] = None, db: Session = Depends(get_db)):
    """Obtener ultimas cotizaciones historicas (INE). Puede filtrar por lista de monedas separadas por comas."""
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

@app.get(ENDPOINT_EXCHANGE_RATE_INFO, tags=[TAG_EXCHANGE])
async def get_exchange_rate_info(db: Session = Depends(get_db)):
    """Informacion del sistema de cotizaciones historicas."""
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
            "data_source": "Central Bank of Uruguay (BCU)"
        }
    
    except Exception as e:
        logger.error(f"Error getting exchange rate information: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get(ENDPOINT_EXCHANGE_RATE_BY_CURRENCY, tags=[TAG_EXCHANGE])
async def get_exchange_rates_by_currency(currency: str, limit: int = 30, db: Session = Depends(get_db)):
    """Obtener historial de una moneda (limite por defecto 30)."""
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

@app.get(ENDPOINT_EXCHANGE_RATE_RANGE, tags=[TAG_EXCHANGE])
async def get_exchange_rates_by_range(start_date: date, end_date: date, currency: Optional[str] = None, db: Session = Depends(get_db)):
    """Obtener cotizaciones por rango de fechas (opcional filtrar por moneda)."""
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

@app.post(ENDPOINT_EXCHANGE_RATE_REFRESH, tags=[TAG_EXCHANGE])
async def refresh_exchange_rate_historical_data(db: Session = Depends(get_db)):
    """Actualizar datos historicos de cotizaciones (INE)."""
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


@app.post("/api/exchange-rate/refresh-async", status_code=202, tags=[TAG_EXCHANGE], summary="Iniciar actualizacion historica asincrona")
async def start_exchange_rate_refresh_async(background_tasks: BackgroundTasks):
    """Inicia la actualizacion historica de cotizaciones en segundo plano (202 Accepted)."""
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


@app.get("/api/jobs/{job_id}", tags=[TAG_EXCHANGE], summary="Estado de un job")
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


@app.get("/api/jobs", tags=[TAG_EXCHANGE], summary="Listado de jobs (debug)")
async def list_jobs():
    # WARNING: In-memory only; suitable for development/testing
    ids = []
    # Access internal structure safely
    for job_id in list(job_manager._jobs.keys()):  # type: ignore[attr-defined]
        job = job_manager.get(job_id)
        if job:
            ids.append({"job_id": job_id, "type": job["type"], "status": job["status"]})
    return {"jobs": ids}


@app.get("/api/exchange-rate/refresh-status/{job_id}", tags=[TAG_EXCHANGE], summary="Alias estado refresh historico")
async def get_exchange_refresh_status(job_id: str):
    return await get_job_status(job_id)


@app.get("/api/exchange-rate/current", tags=[TAG_EXCHANGE])
async def get_current_exchange_rates(force_refresh: bool = False):
    """Obtener cotizaciones actuales (BCU tiempo real)."""
    try:
        # Refresh cache if forced or stale (>55m) or missing
        global bcu_cache
        with _cache_lock:
            cached = bcu_cache
        need_update = False
        if not cached:
            need_update = True
        else:
            age = (datetime.utcnow() - cached.get("updated_at", datetime.utcnow())).total_seconds()
            if age > 55 * 60:
                need_update = True
        if force_refresh or need_update:
            _update_bcu_cache()
            with _cache_lock:
                if bcu_cache is None:  # mocked case
                    bcu_cache = {"data": [], "updated_at": datetime.utcnow()}
                cached = bcu_cache

        if cached:
            return ExchangeRateResponse(
                success=True,
                message=f"Current exchange rates (cached) retrieved successfully. {len(cached['data'])} currencies",
                data=cached["data"]
            ).dict()
        return ExchangeRateResponse(
            success=False,
            message="Could not retrieve current exchange rates",
            data=None
        ).dict()
    
    except Exception as e:
        logger.error(f"Error getting current exchange rates: {e}")
        return ExchangeRateResponse(
            success=False,
            message=f"Internal error: {str(e)}",
            data=None
        ).dict()

@app.get(ENDPOINT_EXCHANGE_RATE_BY_DATE, tags=[TAG_EXCHANGE])
async def get_exchange_rates_by_date(date: date, currency: Optional[str] = None, db: Session = Depends(get_db)):
    """Obtener cotizaciones por fecha especifica (busca fecha mas cercana si no existe)."""
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

@app.get(ENDPOINT_EXCHANGE_RATE_BY_DATE_CURRENCY, tags=[TAG_EXCHANGE])
async def get_exchange_rate_by_date_and_currency(date: date, currency: str, db: Session = Depends(get_db)):
    """Obtener cotizacion especifica (fecha + moneda)."""
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

@app.get("/api/brou/current", tags=["BROU"])
async def get_current_brou_rates(force_refresh: bool = False, full: bool = False):
    """Obtener cotizaciones actuales del BROU.

    Compatibilidad: versión anterior devolvía lista directamente. Ahora por defecto
    seguimos retornando únicamente la lista (para no romper frontend/tests existentes).
    Si se pasa ?full=true se entrega un envoltorio con metadatos.
    """
    try:
        global brou_cache
        with _cache_lock:
            cached = brou_cache
        need_update = False
        if not cached:
            need_update = True
        else:
            age = (datetime.utcnow() - cached.get("updated_at", datetime.utcnow())).total_seconds()
            if age > 55 * 60:
                need_update = True
        if force_refresh or need_update:
            _update_brou_cache()
            with _cache_lock:
                if brou_cache is None:  # mocked case
                    brou_cache = {"data": [], "updated_at": datetime.utcnow()}
                cached = brou_cache

        data_list = cached["data"] if cached else []
        if full:
            return {
                "success": True if data_list else False,
                "message": f"Cotizaciones BROU obtenidas ({len(data_list)} monedas)" if data_list else "Sin datos BROU",
                "data": data_list,
                "source": "BROU",
                "timestamp": datetime.utcnow().isoformat()
            }
        return data_list
    except Exception as e:
        logger.error(f"Error getting current BROU rates: {e}")
        if full:
            return {"success": False, "message": f"Error interno: {str(e)}", "data": None}
        return []


# -----------------------------------------------------------------------------
# __main__ entrypoint (used only for local development / test coverage)
# -----------------------------------------------------------------------------
if __name__ == "__main__":  # pragma: no cover (explicitly exercised in tests)
    import uvicorn  # local import to avoid mandatory dependency at import time
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)