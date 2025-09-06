#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import date, datetime
import asyncio
from typing import Optional
import uuid
import time
import os

from threading import Lock
from threading import Lock as ThreadLock
from bootstrap import perform_bootstrap

from database import get_db
from database_optimizer import DatabaseOptimizer
from models import UIResponse, RefreshResponse, URResponse, ExchangeRateResponse
from services import UIService, URService, ExchangeRateService
from excel_processor import (
    ExcelProcessor,
    URExcelProcessor,
    ExchangeRateExcelProcessor,
    ExchangeRateBCUProcessor,
)
from brou_processor import BROUProcessor
from security_utils import SecurityValidator, InputValidator
from pydantic_models import URRangeRequestModel

# HTTPS Security Middleware
from https_middleware import HTTPSRedirectMiddleware, SSLHeadersMiddleware

# Authentication and Authorization
from auth_routes import router as auth_router
from rate_limit import RateLimitMiddleware, EndpointRateLimitMiddleware
from circuit_breaker import (
    get_all_circuit_breakers,
    get_circuit_breaker_status,
    reset_circuit_breaker,
)

# Metrics middleware
from metrics_middleware import (
    MetricsMiddleware,
    get_metrics,
    get_health,
    get_simple_metrics,
)

# Advanced health checks
from health_checks import get_advanced_health, get_simple_health
from constants import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
    VALID_CURRENCY_CODES,
    CORS_ALLOW_HEADERS,
    CORS_ALLOW_METHODS,
    CORS_ALLOW_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    API_DOCS_URL,
    API_REDOC_URL,
    API_DESCRIPTION,
    API_VERSION,
    API_TITLE,
    CRON_UR_REFRESH,
    CRON_EXCHANGE_REFRESH,
    CRON_UI_REFRESH,
    SCHEDULER_ENABLED,
    SCHEDULER_TIMEZONE,
    ENDPOINT_HEALTH,
    STATIC_DIRECTORY,
    STATIC_MOUNT_PATH,
    STATIC_NAME,
    TAG_EXCHANGE,
    TAG_UR,
    TAG_UI,
    MSG_EXCHANGE_RATE_DATE_SUCCESS,
    MSG_EXCHANGE_RATE_CURRENCY_SUCCESS,
    MSG_LATEST_EXCHANGE_RATE_SUCCESS,
    MSG_NO_EXCHANGE_RATE_DATE_DATA,
    MSG_NO_UR_RANGE_DATA,
    MSG_UR_RANGE_SUCCESS,
    MSG_INVALID_MONTH,
    MSG_INVALID_PERIOD_RANGE,
    MSG_UI_RANGE_SUCCESS,
    MSG_LATEST_UI_SUCCESS,
    MSG_NO_UI_DATA,
    MSG_UI_DATE_SUCCESS,
    MSG_NO_UR_YEAR_DATA,
    MSG_NO_UR_DATA,
    MSG_LATEST_UR_SUCCESS,
    MSG_UR_YEAR_SUCCESS,
    MSG_UR_YEAR_MONTH_SUCCESS,
    MSG_NO_EXCHANGE_RATE_CURRENCY_DATA,
    MSG_NO_EXCHANGE_RATE_DATA,
    MSG_NO_UR_YEAR_MONTH_DATA,
    MSG_EXCHANGE_RATE_RANGE_SUCCESS,
    ENDPOINT_EXCHANGE_RATE_BY_DATE_CURRENCY,
    ENDPOINT_EXCHANGE_RATE_BY_DATE,
    ENDPOINT_EXCHANGE_RATE_REFRESH,
    ENDPOINT_EXCHANGE_RATE_BY_CURRENCY,
    ENDPOINT_EXCHANGE_RATE_INFO,
    ENDPOINT_EXCHANGE_RATE_LATEST,
    ENDPOINT_EXCHANGE_RATE_RANGE,
    SCHEDULER_BUSINESS_DAY_ONLY,
    SCHEDULER_HOLIDAYS,
    CRON_EXCHANGE_HOURLY_CHECK,
    CRON_DATA_GUARD,
    EXCHANGE_HOURLY_CHECK_ENABLED,
    EXCHANGE_HOURLY_CHECK_START_HOUR,
    EXCHANGE_HOURLY_CHECK_END_HOUR,
    DATA_GUARD_UI_COOLDOWN_MIN,
    DATA_GUARD_UR_COOLDOWN_MIN,
    DATA_GUARD_EXCHANGE_COOLDOWN_MIN,
)

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

# Correlation ID middleware for distributed tracing
from correlation_middleware import (
    CorrelationIdMiddleware,
    setup_correlation_logging,
    get_correlation_logger,
)

# Alert and dashboard services
from alerts import alert_manager
from dashboard import dashboard_service

# Configure correlation logging
setup_correlation_logging()
logger = get_correlation_logger(__name__)

# Performance budget service
try:
    from performance_budget import get_performance_budget_manager

    # Reactivar performance budget manager con configuración segura
    performance_budget_manager = get_performance_budget_manager(
        enable_monitoring=False, enable_alerts=False
    )
    logger.info("Performance budget manager reactivated successfully")
except ImportError:
    logger.warning("Performance budget module not available")
    performance_budget_manager = None
except Exception as e:
    logger.error(f"Error initializing performance budget manager: {e}")
    performance_budget_manager = None

# Flag para omitir bootstrap y refresh en startup (usado en tests / CI)
SKIP_BOOTSTRAP = os.getenv("SIFU_SKIP_BOOTSTRAP") == "1"


# Lifespan context replacing deprecated on_event startup/shutdown
async def _execute_startup():
    """Reusable startup logic; safe to call multiple times in tests."""
    logger.info("Starting SIFU (bootstrap + cache warmup)... skip=%s", SKIP_BOOTSTRAP)
    global scheduler

    try:
        # Minimal phase: siempre instanciamos servicio y consultamos total para que los tests
        # puedan verificar la llamada (incluso cuando SKIP_BOOTSTRAP=1)
        db = None
        try:
            from database import (
                SessionLocal as _SL,
            )  # local import para evitar costos al importar tests

            db = _SL()
            service = UIService(db)
            total = service.get_total_records()  # <- los tests esperan que se llame
            if total == 0:
                if os.getenv("SIFU_SKIP_STARTUP_REFRESH") == "1":
                    logger.info(
                        "[Startup] Refresh suprimido (SIFU_SKIP_STARTUP_REFRESH=1)"
                    )
                else:
                    try:
                        excel_processor.refresh_data(db)
                    except Exception as e:  # noqa: BLE001
                        logger.error(f"[LegacyBootstrap] UI refresh failed: {e}")
            else:
                logger.info(f"[Startup] UI data present ({total} records)")
        except Exception as e:  # noqa: BLE001
            logger.error(f"[LegacyBootstrap] skipped due to error: {e}")
        finally:
            if db:
                try:
                    db.close()
                except Exception:  # noqa: BLE001
                    pass

        # Si skip activado, no continuamos con bootstrap pesado / caches / scheduler
        if SKIP_BOOTSTRAP:
            logger.info("[Startup] Bootstrap pesado omitido (skip flag)")
            return

        # Full bootstrap (solo si no skip)
        try:
            summary = perform_bootstrap(
                force=False,
                excel_processor=excel_processor,
                ur_excel_processor=ur_excel_processor,
                exchange_rate_excel_processor=exchange_rate_excel_processor,
            )
            logger.info(f"[Bootstrap] summary={summary}")
        except Exception as e:  # noqa: BLE001
            logger.error(f"[Bootstrap] failed: {e}")

        # Warm caches
        try:
            _update_bcu_cache()
            _update_brou_cache()
        except Exception as e:  # noqa: BLE001
            logger.error(f"Cache warmup failed: {e}")

        # Initialize database optimizer (skip in test environment)
        is_test_env = (
            os.getenv("PYTEST_CURRENT_TEST") is not None
            or os.getenv("TESTING") == "true"
            or "pytest" in os.getenv("_", "").lower()
        )

        if not is_test_env:
            try:
                optimizer = DatabaseOptimizer()
                logger.info(
                    "[DatabaseOptimizer] Initializing database optimizations..."
                )
                optimizer.create_optimized_indexes()
                logger.info("[DatabaseOptimizer] Database optimizations completed")
            except Exception as e:  # noqa: BLE001
                logger.error(f"[DatabaseOptimizer] Initialization failed: {e}")
        else:
            logger.info(
                "[DatabaseOptimizer] Skipping database optimizations in test environment"
            )

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
        global scheduler
        if scheduler is None:
            try:
                if SCHEDULER_ENABLED and CronTrigger:
                    # Try AsyncIOScheduler again to see if it works with middlewares disabled
                    from apscheduler.schedulers.asyncio import AsyncIOScheduler

                    scheduler = AsyncIOScheduler(timezone=SCHEDULER_TIMEZONE)
                    _add_jobs(scheduler)
                    scheduler.start()
                    logger.info(
                        f"[Scheduler] Started with AsyncIOScheduler (tz={SCHEDULER_TIMEZONE})"
                    )
                else:
                    logger.info("[Scheduler] Disabled or APScheduler not installed")
            except Exception as e:  # noqa: BLE001
                logger.error(f"[Scheduler] Failed to start: {e}")

        logger.info("Startup bootstrap complete")

    except Exception as e:
        logger.error(f"[Startup] CRITICAL ERROR during startup: {e}")
        logger.error(f"[Startup] Exception type: {type(e)}")
        import traceback

        logger.error(f"[Startup] Traceback: {traceback.format_exc()}")
        # Re-raise to let FastAPI handle it properly
        raise


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
    lifespan=app_lifespan,
    tags_metadata=[
        {
            "name": "Sistema",
            "description": "Endpoints de sistema: health check e informacion general",
        },
        {
            "name": TAG_UI,
            "description": (
                "Consulta de valores de la Unidad Indexada del Instituto Nacional de Estadistica (INE). "
                "La UI es un indice de ajuste por inflacion utilizado en Uruguay desde 2002."
            ),
        },
        {
            "name": TAG_UR,
            "description": (
                "Consulta de valores de la Unidad Reajustable del Banco Hipotecario del Uruguay (BHU). "
                "La UR es un indice utilizado para reajustar creditos hipotecarios desde 1969."
            ),
        },
        {
            "name": TAG_EXCHANGE,
            "description": (
                "Sistema dual de cotizaciones: datos historicos del INE (2001-presente) y "
                "cotizaciones actuales del BCU en tiempo real. Incluye USD, EUR, ARS, BRL."
            ),
        },
        {
            "name": "BROU",
            "description": (
                "Cotizaciones del Banco de la Republica Oriental del Uruguay (BROU). "
                "Incluye USD, USD eBROU, EUR, ARS, BRL con valores de compra/venta y arbitrajes."
            ),
        },
    ],
)

# Add correlation ID middleware (must be first)
app.add_middleware(CorrelationIdMiddleware)

# Add HTTPS security middlewares
app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(SSLHeadersMiddleware)

# Configure CORS to allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)

# Add security middlewares
app.add_middleware(RateLimitMiddleware, requests_per_minute=100, burst_limit=20)
app.add_middleware(EndpointRateLimitMiddleware)

# Add metrics middleware
app.add_middleware(MetricsMiddleware)

# Include authentication router
app.include_router(auth_router)


@app.get("/api/debug/correlation", tags=["Sistema"])
async def debug_correlation_id(request: Request):
    """Endpoint de debug para probar correlation IDs."""
    from correlation_middleware import get_correlation_id

    correlation_id = get_correlation_id(request)
    logger.info(f"Debug endpoint called with correlation ID: {correlation_id}")

    return {
        "correlation_id": correlation_id,
        "message": "Check server logs for correlation ID tracing",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/test", tags=["Sistema"])
async def test_endpoint():
    """Endpoint de prueba simple sin dependencias."""
    return {
        "message": "Test endpoint working",
        "timestamp": datetime.utcnow().isoformat(),
    }


# -----------------------------------------------------------------------------
# Scheduler setup (optional)
# -----------------------------------------------------------------------------
scheduler: Any = None


def _add_jobs(_scheduler):
    tz = pytz.timezone(SCHEDULER_TIMEZONE) if pytz else None

    def _is_business_day(today: datetime | None = None) -> bool:
        """Return True if today is a business day (Mon-Fri and not in holidays)."""
        today = today or datetime.utcnow()
        if not SCHEDULER_BUSINESS_DAY_ONLY:
            return True
        iso = today.date().isoformat()
        if iso in SCHEDULER_HOLIDAYS:
            return False
        # weekday(): Mon=0 .. Sun=6
        return today.weekday() < 5

    # UI daily refresh
    def job_ui_refresh():
        try:
            if not _is_business_day():
                logger.info("[Scheduler][UI] Skipped (non-business day)")
                return
            from database import SessionLocal

            db = SessionLocal()
            logger.info("[Scheduler] Running UI refresh job...")
            success, message, total_records = excel_processor.refresh_data(db)
            logger.info(
                f"[Scheduler][UI] success={success} msg='{message}' total_records={total_records}"
            )
            db.close()
        except Exception as e:
            logger.error(f"[Scheduler][UI] error: {e}")

    # Exchange historical daily refresh
    def job_exchange_refresh():
        try:
            if not _is_business_day():
                logger.info("[Scheduler][EXCHANGE] Skipped (non-business day)")
                return
            from database import SessionLocal

            db = SessionLocal()
            logger.info("[Scheduler] Running Exchange refresh job...")
            success, message, total_records = (
                exchange_rate_excel_processor.refresh_data(db)
            )
            logger.info(
                f"[Scheduler][EXCHANGE] success={success} msg='{message}' total_records={total_records}"
            )
            db.close()
        except Exception as e:
            logger.error(f"[Scheduler][EXCHANGE] error: {e}")

    # Hourly check (only within configured hour window). If latest date < today (weekday) attempt refresh.
    def job_exchange_hourly_check():
        if not EXCHANGE_HOURLY_CHECK_ENABLED:
            return
        now = datetime.now()
        hour = now.hour
        if (
            hour < EXCHANGE_HOURLY_CHECK_START_HOUR
            or hour > EXCHANGE_HOURLY_CHECK_END_HOUR
        ):
            return
        try:
            if not _is_business_day(now):
                return
            from database import SessionLocal

            db = SessionLocal()
            service = ExchangeRateService(db)
            _min, max_date = service.get_date_range_available()
            if max_date is None:
                logger.info("[Scheduler][EXCHANGE_CHECK] No data, triggering refresh")
                exchange_rate_excel_processor.refresh_data(db)
            else:
                today = now.date()
                if max_date < today:
                    logger.info(
                        f"[Scheduler][EXCHANGE_CHECK] Data stale (max={max_date}), attempting refresh"
                    )
                    exchange_rate_excel_processor.refresh_data(db)
                else:
                    logger.debug(
                        f"[Scheduler][EXCHANGE_CHECK] Data up-to-date (max={max_date})"
                    )
            db.close()
        except Exception as e:  # noqa: BLE001
            logger.error(f"[Scheduler][EXCHANGE_CHECK] error: {e}")

    # UR monthly refresh
    def job_ur_refresh():
        try:
            # UR es mensual; si cae fin de semana se ejecutará el primer día hábil siguiente (no aplicamos skip aquí)
            from database import SessionLocal

            db = SessionLocal()
            logger.info("[Scheduler] Running UR refresh job...")
            success, message, count = ur_excel_processor.refresh_data(db)
            logger.info(
                f"[Scheduler][UR] success={success} msg='{message}' count={count}"
            )
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
        return CronTrigger(
            minute=minute, hour=hour, day=day, month=month, day_of_week=dow, timezone=tz
        )

    # Data freshness guard (every few minutes) - forces refresh if expected new data missing
    _data_guard_last_attempt: dict[str, datetime] = {}

    def job_data_freshness_guard():
        now_local = datetime.now(tz)
        from database import SessionLocal

        db = None
        try:
            db = SessionLocal()
            # UI: daily value expected on business days after 02:30 local
            try:
                ui_service = UIService(db)
                latest_ui = ui_service.get_latest_ui()
                today = now_local.date()
                need_ui = False
                if latest_ui is None:
                    need_ui = True
                else:
                    if (
                        latest_ui.date < today
                        and now_local.hour >= 2
                        and now_local.minute >= 30
                        and now_local.weekday() < 5
                    ):
                        need_ui = True
                if need_ui:
                    last_try = _data_guard_last_attempt.get("ui")
                    if (
                        not last_try
                        or (now_local - last_try).total_seconds() / 60
                        >= DATA_GUARD_UI_COOLDOWN_MIN
                    ):
                        logger.info(
                            "[DataGuard][UI] Forcing refresh (latest=%s)"
                            % (latest_ui.date if latest_ui else "None")
                        )
                        excel_processor.refresh_data(db)
                        _data_guard_last_attempt["ui"] = now_local
                    else:
                        # Cooldown active
                        elapsed = (now_local - last_try).total_seconds() / 60
                        logger.debug(
                            "[DataGuard][UI] Cooldown active (elapsed=%.1fm < %dm, latest=%s)"
                            % (
                                elapsed,
                                DATA_GUARD_UI_COOLDOWN_MIN,
                                latest_ui.date if latest_ui else "None",
                            )
                        )
                else:
                    # Explicit log for visibility when no action needed
                    logger.debug(
                        "[DataGuard][UI] Up-to-date (latest=%s today=%s now=%s)"
                        % (
                            latest_ui.date if latest_ui else "None",
                            today,
                            now_local.strftime("%H:%M"),
                        )
                    )
            except Exception as e:  # noqa: BLE001
                logger.error(f"[DataGuard][UI] error: {e}")

            # UR: monthly value expected at month change (first business day after day 1) after 08:00
            try:
                ur_service = URService(db)
                latest_ur = ur_service.get_latest_ur()
                year = now_local.year
                month = now_local.month

                def _first_business_day(y, m):
                    for d in range(1, 8):
                        dt = date(y, m, d)
                        if dt.weekday() < 5:  # Mon-Fri
                            return dt
                    return date(y, m, 1)

                first_bd = _first_business_day(year, month)
                need_ur = False
                if latest_ur is None:
                    need_ur = True
                else:
                    # Compare tuples (year, month)
                    if (
                        (latest_ur.year, latest_ur.month) < (year, month)
                        and now_local.date() >= first_bd
                        and now_local.hour >= 8
                    ):
                        need_ur = True
                if need_ur:
                    last_try = _data_guard_last_attempt.get("ur")
                    if (
                        not last_try
                        or (now_local - last_try).total_seconds() / 60
                        >= DATA_GUARD_UR_COOLDOWN_MIN
                    ):
                        logger.info(
                            "[DataGuard][UR] Forcing refresh (latest=%s-%s)"
                            % (
                                (latest_ur.year, latest_ur.month)
                                if latest_ur
                                else ("None", "")
                            )
                        )
                        ur_excel_processor.refresh_data(db)
                        _data_guard_last_attempt["ur"] = now_local
                    else:
                        elapsed = (now_local - last_try).total_seconds() / 60
                        logger.debug(
                            "[DataGuard][UR] Cooldown active (elapsed=%.1fm < %dm, latest=%s-%s)"
                            % (
                                elapsed,
                                DATA_GUARD_UR_COOLDOWN_MIN,
                                latest_ur.year if latest_ur else "None",
                                latest_ur.month if latest_ur else "",
                            )
                        )
                else:
                    logger.debug(
                        "[DataGuard][UR] Up-to-date (latest=%s current=%s first_bd=%s now=%s)"
                        % (
                            (f"{latest_ur.year}-{latest_ur.month:02d}") if latest_ur else "None",
                            f"{year}-{month:02d}",
                            first_bd.isoformat(),
                            now_local.strftime("%H:%M"),
                        )
                    )
            except Exception as e:  # noqa: BLE001
                logger.error(f"[DataGuard][UR] error: {e}")

            # Exchange historical daily (similar to existing daily job) – if latest date < today after 11:00
            try:
                ex_service = ExchangeRateService(db)
                _min, ex_max = ex_service.get_date_range_available()
                today = now_local.date()
                need_ex = False
                if ex_max is None:
                    need_ex = True
                else:
                    if ex_max < today and now_local.hour >= 11:
                        need_ex = True
                if need_ex:
                    last_try = _data_guard_last_attempt.get("exchange")
                    if (
                        not last_try
                        or (now_local - last_try).total_seconds() / 60
                        >= DATA_GUARD_EXCHANGE_COOLDOWN_MIN
                    ):
                        logger.info(
                            f"[DataGuard][EXCHANGE] Forcing refresh (latest={ex_max})"
                        )
                        exchange_rate_excel_processor.refresh_data(db)
                        _data_guard_last_attempt["exchange"] = now_local
                    else:
                        elapsed = (now_local - last_try).total_seconds() / 60
                        logger.debug(
                            "[DataGuard][EXCHANGE] Cooldown active (elapsed=%.1fm < %dm, latest=%s)"
                            % (
                                elapsed,
                                DATA_GUARD_EXCHANGE_COOLDOWN_MIN,
                                ex_max if ex_max else "None",
                            )
                        )
                else:
                    logger.debug(
                        "[DataGuard][EXCHANGE] Up-to-date (latest=%s today=%s now=%s)"
                        % (
                            ex_max if ex_max else "None",
                            today,
                            now_local.strftime("%H:%M"),
                        )
                    )
            except Exception as e:  # noqa: BLE001
                logger.error(f"[DataGuard][EXCHANGE] error: {e}")
        except Exception as e:  # noqa: BLE001
            logger.error(f"[DataGuard] unexpected error: {e}")
        finally:
            try:
                if db:
                    db.close()
            except Exception:
                pass

    _scheduler.add_job(
        job_ui_refresh, _cron(CRON_UI_REFRESH), id="ui_refresh", replace_existing=True
    )
    _scheduler.add_job(
        job_exchange_refresh,
        _cron(CRON_EXCHANGE_REFRESH),
        id="exchange_refresh",
        replace_existing=True,
    )
    _scheduler.add_job(
        job_ur_refresh, _cron(CRON_UR_REFRESH), id="ur_refresh", replace_existing=True
    )
    # Data guard job (every few minutes)
    try:
        _scheduler.add_job(
            job_data_freshness_guard,
            _cron(CRON_DATA_GUARD),
            id="data_guard",
            replace_existing=True,
        )
    except Exception as e:  # noqa: BLE001
        logger.error(f"[Scheduler] Could not schedule data_guard: {e}")
    if EXCHANGE_HOURLY_CHECK_ENABLED:
        _scheduler.add_job(
            job_exchange_hourly_check,
            _cron(CRON_EXCHANGE_HOURLY_CHECK),
            id="exchange_hourly_check",
            replace_existing=True,
        )
    logger.info(
        "[Scheduler] Jobs scheduled: ui_refresh, exchange_refresh, ur_refresh, data_guard"
        + (", exchange_hourly_check" if EXCHANGE_HOURLY_CHECK_ENABLED else "")
    )


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
            formatted.append(
                {
                    "currency": currency,
                    "buy_rate": buy,
                    "sell_rate": sell,
                    "average_rate": avg,
                    "source": source,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
        with _cache_lock:
            bcu_cache = {"data": formatted, "updated_at": datetime.utcnow()}
        logger.info(f"[BCU Cache] Updated ({len(formatted)} currencies)")
    except Exception as e:
        logger.error(f"[BCU Cache] Update failed: {e}")


def _update_brou_cache():
    global brou_cache
    try:
        current_rates, is_from_brou, source_type = brou_processor.get_current_rates()
        if not current_rates:
            logger.warning("[BROU Cache] No data fetched")
            return

        # Map source_type to user-friendly source name
        source_map = {
            "live": "BROU",
            "persisted": "BROU_PERSISTED",
            "sample": "BROU_SAMPLE",
        }
        source = source_map.get(source_type, f"BROU_{source_type.upper()}")

        formatted: list[dict] = []
        for rate in current_rates:
            # rate es un dict según BROUProcessor._get_sample_rates / get_current_rates
            try:
                currency = rate.get("currency")
                if not currency:
                    continue
                formatted.append(
                    {
                        "currency": currency,
                        "buy_rate": rate.get("buy_rate"),
                        "sell_rate": rate.get("sell_rate"),
                        "average_rate": rate.get("average_rate"),
                        "arbitrage_buy": rate.get("arbitrage_buy"),
                        "arbitrage_sell": rate.get("arbitrage_sell"),
                        # Preferencial: marcar USD_EBROU
                        "preferential": True if currency == "USD_EBROU" else None,
                        "source": source,
                        "timestamp": rate.get("timestamp")
                        or datetime.utcnow().isoformat(),
                    }
                )
            except Exception as e:  # noqa: BLE001
                logger.error(f"[BROU Cache] Skipping rate due to error: {e}")
        if not formatted:
            logger.warning(
                "[BROU Cache] No valid rate entries after formatting. Using sample fallback."
            )
            try:
                sample_rates = brou_processor._get_sample_rates()  # noqa: SLF001 (internal fallback)
                for rate in sample_rates:
                    currency = rate.get("currency")
                    if not currency:
                        continue
                    formatted.append(
                        {
                            "currency": currency,
                            "buy_rate": rate.get("buy_rate"),
                            "sell_rate": rate.get("sell_rate"),
                            "average_rate": rate.get("average_rate"),
                            "arbitrage_buy": rate.get("arbitrage_buy"),
                            "arbitrage_sell": rate.get("arbitrage_sell"),
                            "preferential": True if currency == "USD_EBROU" else None,
                            "source": "BROU_SAMPLE",
                            "timestamp": rate.get("timestamp")
                            or datetime.utcnow().isoformat(),
                        }
                    )
            except Exception as fe:  # noqa: BLE001
                logger.error(f"[BROU Cache] Fallback sample failed: {fe}")
                return
        with _cache_lock:
            brou_cache = {
                "data": formatted,
                "updated_at": datetime.utcnow(),
                "source": source,
                "source_type": source_type,
            }
        logger.info(f"[BROU Cache] Updated ({len(formatted)} currencies) from {source}")
    except Exception as e:
        logger.error(f"[BROU Cache] Update failed: {e}")


# =============================================================================
# Simple in-memory job manager for long-running tasks (exchange historical refresh)
# =============================================================================


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
                if meta["type"] == job_type and meta["status"] in (
                    JobStatus.PENDING,
                    JobStatus.RUNNING,
                ):
                    return jid
        return None


job_manager = JobManager()


# Mount static files only if they exist
if os.path.exists(STATIC_DIRECTORY):
    app.mount(
        STATIC_MOUNT_PATH, StaticFiles(directory=STATIC_DIRECTORY), name=STATIC_NAME
    )


@app.get(ENDPOINT_HEALTH, tags=["Sistema"])
async def health_check():
    """Health check básico del sistema.

    Verifica que el servicio esté funcionando correctamente.
    Para health checks avanzados usar /api/health/advanced
    """
    from datetime import datetime

    return {
        "status": "ok",
        "message": "Server is running",
        "timestamp": datetime.utcnow().isoformat(),
    }


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
                data=latest_ui.dict() if hasattr(latest_ui, "dict") else latest_ui,
            ).dict()
        else:
            return UIResponse(success=False, message=MSG_NO_UI_DATA).dict()

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
                data=ui_value.dict() if hasattr(ui_value, "dict") else ui_value,
            ).dict()
        else:
            # Try to find the closest value
            closest_ui = service.get_ui_closest_to_date(date)
            if closest_ui:
                return UIResponse(
                    success=True,
                    message=f"No data for {date}. Showing closest previous value",
                    data=closest_ui.dict()
                    if hasattr(closest_ui, "dict")
                    else closest_ui,
                ).dict()
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"No UI data found for {date} or previous dates",
                )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting UI by date {date}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ui/range/{start_date}/{end_date}", tags=[TAG_UI])
async def get_ui_by_range(
    start_date: date, end_date: date, db: Session = Depends(get_db)
):
    """Obtener UI por rango de fechas (YYYY-MM-DD).

    Valida que start_date <= end_date.
    """
    try:
        if start_date > end_date:
            raise HTTPException(
                status_code=400,
                detail="Start date must be less than or equal to end date",
            )

        service = UIService(db)
        ui_values = service.get_ui_by_date_range(start_date, end_date)

        return UIResponse(
            success=True,
            message=MSG_UI_RANGE_SUCCESS.format(
                start_date=start_date, end_date=end_date, count=len(ui_values)
            ),
            data=[item.dict() if hasattr(item, "dict") else item for item in ui_values],
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
                "max_date": max_date.isoformat() if max_date else None,
            },
            "latest_ui": latest_ui.dict() if latest_ui else None,
            "data_source": "National Institute of Statistics (INE) - Uruguay",
        }

    except Exception as e:
        logger.error(f"Error getting information: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/refresh", tags=[TAG_UI])
async def refresh_data(
    background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
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
                last_updated=latest_ui.date if latest_ui else None,
            ).dict()
        else:
            return RefreshResponse(
                success=False, message=message, total_records=0
            ).dict()

    except Exception as e:
        logger.error(f"Error updating data: {e}")
        return RefreshResponse(
            success=False, message=f"Internal error: {str(e)}", total_records=0
        )


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
                data=latest_ur.dict() if hasattr(latest_ur, "dict") else latest_ur,
            ).dict()
        else:
            return URResponse(success=False, message=MSG_NO_UR_DATA, data=None).dict()

    except Exception as e:
        logger.error(f"Error in get_latest_ur: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/ur/year-month/{year}/{month}", tags=[TAG_UR])
async def get_ur_by_year_month(year: int, month: int, db: Session = Depends(get_db)):
    """Obtener UR por anio y mes (YYYY, 1-12)."""
    try:
        # Validate month
        if month < 1 or month > 12:
            return URResponse(
                success=False, message="Month must be between 1 and 12", data=None
            ).dict()

        ur_service = URService(db)
        ur_value = ur_service.get_ur_by_year_month(year, month)

        if ur_value:
            return URResponse(
                success=True,
                message=MSG_UR_YEAR_MONTH_SUCCESS.format(year=year, month=month),
                data=ur_value.dict() if hasattr(ur_value, "dict") else ur_value,
            ).dict()
        else:
            return URResponse(
                success=False,
                message=MSG_NO_UR_YEAR_MONTH_DATA.format(year=year, month=month),
                data=None,
            ).dict()

    except Exception as e:
        logger.error(f"Error in get_ur_by_year_month: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


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
                data=[
                    item.dict() if hasattr(item, "dict") else item for item in ur_values
                ],
            ).dict()
        else:
            return URResponse(
                success=False, message=MSG_NO_UR_YEAR_DATA.format(year=year), data=[]
            ).dict()

    except Exception as e:
        logger.error(f"Error in get_ur_by_year: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get(
    "/api/ur/range/{start_year}/{start_month}/{end_year}/{end_month}", tags=[TAG_UR]
)
async def get_ur_by_range(
    start_year: int,
    start_month: int,
    end_year: int,
    end_month: int,
    db: Session = Depends(get_db),
):
    """Obtener UR por rango de periodos (anio/mes inicio a anio/mes fin)."""
    try:
        # Validate months
        if start_month < 1 or start_month > 12 or end_month < 1 or end_month > 12:
            return URResponse(
                success=False,
                message=MSG_INVALID_MONTH
                if "MSG_INVALID_MONTH" in globals()
                else "Months must be between 1 and 12",
                data=None,
            ).dict()

        # Validate range
        if (start_year > end_year) or (
            start_year == end_year and start_month > end_month
        ):
            return URResponse(
                success=False, message=MSG_INVALID_PERIOD_RANGE, data=None
            ).dict()

        ur_service = URService(db)
        ur_values = ur_service.get_ur_by_range(
            start_year, start_month, end_year, end_month
        )

        if ur_values:
            return URResponse(
                success=True,
                message=MSG_UR_RANGE_SUCCESS.format(
                    count=len(ur_values),
                    start_year=start_year,
                    start_month=start_month,
                    end_year=end_year,
                    end_month=end_month,
                ),
                data=[
                    item.dict() if hasattr(item, "dict") else item for item in ur_values
                ],
            ).dict()
        else:
            return URResponse(
                success=False,
                message=MSG_NO_UR_RANGE_DATA.format(
                    start_year=start_year,
                    start_month=start_month,
                    end_year=end_year,
                    end_month=end_month,
                ),
                data=[],
            ).dict()

    except Exception as e:
        logger.error(f"Error in get_ur_by_range: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/ur/range", tags=[TAG_UR])
async def get_ur_by_range_post(request: dict, db: Session = Depends(get_db)):
    """Obtener UR por rango (POST). Body igual al endpoint GET correspondiente."""
    try:
        # Convert Spanish field names to English
        field_mapping = {
            "año_inicio": "start_year",
            "mes_inicio": "start_month",
            "año_fin": "end_year",
            "mes_fin": "end_month",
        }

        # Create sanitized data with English field names
        sanitized_data = {}
        for key, value in request.items():
            english_key = field_mapping.get(key, key)
            sanitized_data[english_key] = value

        # Validate with Pydantic model
        ur_request = URRangeRequestModel(**sanitized_data)

        # Additional security validation
        is_valid, error_msg = InputValidator.validate_ur_range_params(
            ur_request.start_year,
            ur_request.start_month,
            ur_request.end_year,
            ur_request.end_month,
        )

        if not is_valid:
            return URResponse(success=False, message=error_msg).dict()

        # Check for injection attempts
        for key, value in sanitized_data.items():
            if isinstance(value, str) and not SecurityValidator.validate_no_injection(
                value
            ):
                return URResponse(
                    success=False, message="Invalid input detected"
                ).dict()

        return await get_ur_by_range(
            ur_request.start_year,
            ur_request.start_month,
            ur_request.end_year,
            ur_request.end_month,
            db,
        )

    except Exception as e:
        logger.error(f"Error in get_ur_by_range_post: {e}")
        return URResponse(success=False, message="Invalid request format").dict()


@app.post("/api/ur/refresh", tags=[TAG_UR])
async def refresh_ur_data(db: Session = Depends(get_db)):
    """Actualizar datos de UR desde BHU (descarga + procesamiento)."""
    try:
        logger.info("Starting UR data update...")

        success, message, count = ur_excel_processor.refresh_data(db)

        # Get additional information
        ur_service = URService(db)
        total_records = ur_service.get_total_records()

        return RefreshResponse(
            success=success,
            message=message,
            total_records=total_records,
            last_updated=None,  # UR has no specific date, only year-month
        ).dict()

    except Exception as e:
        logger.error(f"Error in refresh_ur_data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/ur/info", tags=[TAG_UR])
async def get_ur_info(db: Session = Depends(get_db)):
    """Informacion del sistema UR (estadisticas basicas)."""
    try:
        ur_service = URService(db)

        total_records = ur_service.get_total_records()
        min_year, max_year = ur_service.get_year_range_available()
        latest_ur = ur_service.get_latest_ur()
        available_years = ur_service.get_available_years()
        # Pending flag if latest year-month < current year-month
        pending = False
        pending_message = None
        try:
            if latest_ur:
                from datetime import datetime as _dt
                now = _dt.utcnow()
                if (latest_ur.year, latest_ur.month) < (now.year, now.month):
                    from constants import MSG_UR_PENDING_CURRENT_MONTH
                    pending = True
                    pending_message = MSG_UR_PENDING_CURRENT_MONTH
        except Exception:
            pass

        return {
            "success": True,
            "data": {
                "total_records": total_records,
                "year_range": {"min_year": min_year, "max_year": max_year},
                "latest_value": latest_ur.dict() if latest_ur else None,
                "available_years": available_years,
                "pending_current_month": pending,
                "pending_message": pending_message,
            },
        }

    except Exception as e:
        logger.error(f"Error in get_ur_info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# =============================================================================
# EXCHANGE RATE ENDPOINTS
# =============================================================================


@app.get(ENDPOINT_EXCHANGE_RATE_LATEST, tags=[TAG_EXCHANGE])
async def get_latest_exchange_rates(
    currencies: Optional[str] = None, db: Session = Depends(get_db)
):
    """Obtener ultimas cotizaciones historicas (INE). Puede filtrar por lista de monedas separadas por comas."""
    try:
        service = ExchangeRateService(db)
        currency_list = currencies.split(",") if currencies else None

        exchange_rates = service.get_latest_exchange_rates(currency_list)

        if exchange_rates:
            return ExchangeRateResponse(
                success=True,
                message=MSG_LATEST_EXCHANGE_RATE_SUCCESS,
                data=[rate.dict() for rate in exchange_rates],
            ).dict()
        else:
            return ExchangeRateResponse(
                success=False, message=MSG_NO_EXCHANGE_RATE_DATA
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
                "max_date": max_date.isoformat() if max_date else None,
            },
            "available_currencies": available_currencies,
            "latest_rates": [rate.dict() for rate in latest_rates],
            "data_source": "Central Bank of Uruguay (BCU)",
        }

    except Exception as e:
        logger.error(f"Error getting exchange rate information: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get(ENDPOINT_EXCHANGE_RATE_BY_CURRENCY, tags=[TAG_EXCHANGE])
async def get_exchange_rates_by_currency(
    currency: str, limit: int = 30, db: Session = Depends(get_db)
):
    """Obtener historial de una moneda (limite por defecto 30)."""
    try:
        if currency.upper() not in VALID_CURRENCY_CODES:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"Invalid currency code. Supported currencies: {', '.join(VALID_CURRENCY_CODES)}",
            )

        service = ExchangeRateService(db)
        exchange_rates = service.get_exchange_rate_by_currency(currency, limit)

        if exchange_rates:
            return ExchangeRateResponse(
                success=True,
                message=MSG_EXCHANGE_RATE_CURRENCY_SUCCESS.format(
                    currency=currency.upper()
                ),
                data=[rate.dict() for rate in exchange_rates],
            ).dict()
        else:
            return ExchangeRateResponse(
                success=False,
                message=MSG_NO_EXCHANGE_RATE_CURRENCY_DATA.format(
                    currency=currency.upper()
                ),
            ).dict()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting exchange rates by currency {currency}: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get(ENDPOINT_EXCHANGE_RATE_RANGE, tags=[TAG_EXCHANGE])
async def get_exchange_rates_by_range(
    start_date: date,
    end_date: date,
    currency: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Obtener cotizaciones por rango de fechas (opcional filtrar por moneda)."""
    try:
        # Validate date range
        is_valid, error_msg = InputValidator.validate_range_params(
            str(start_date), str(end_date)
        )
        if not is_valid:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=error_msg)

        # Validate currency if provided
        if currency:
            is_valid, error_msg = InputValidator.validate_currency_param(currency)
            if not is_valid:
                raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=error_msg)

        service = ExchangeRateService(db)
        exchange_rates = service.get_exchange_rate_by_date_range(
            start_date, end_date, currency
        )

        return ExchangeRateResponse(
            success=True,
            message=MSG_EXCHANGE_RATE_RANGE_SUCCESS.format(
                start_date=start_date, end_date=end_date, count=len(exchange_rates)
            ),
            data=[rate.dict() for rate in exchange_rates],
        ).dict()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error getting exchange rates by range {start_date} - {end_date}: {e}"
        )
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post(ENDPOINT_EXCHANGE_RATE_REFRESH, tags=[TAG_EXCHANGE])
async def refresh_exchange_rate_historical_data(db: Session = Depends(get_db)):
    """Actualizar datos historicos de cotizaciones (INE)."""
    try:
        logger.info(
            "Starting historical exchange rate data update from INE (synchronous endpoint)..."
        )
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
                        "max_date": max_date.isoformat() if max_date else None,
                    },
                },
            ).dict()
        return ExchangeRateResponse(success=False, message=message, data=None).dict()
    except Exception as e:
        logger.error(f"Error refreshing historical exchange rate data: {e}")
        return ExchangeRateResponse(
            success=False, message=f"Internal error: {str(e)}", data=None
        ).dict()


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
        success, message, total_records = exchange_rate_excel_processor.refresh_data(
            db_local
        )
        if success:
            service = ExchangeRateService(db_local)
            total_db_records = service.get_total_records()
            min_date, max_date = service.get_date_range_available()
            result_summary = {
                "total_records": total_records,
                "total_db_records": total_db_records,
                "date_range": {
                    "min_date": min_date.isoformat() if min_date else None,
                    "max_date": max_date.isoformat() if max_date else None,
                },
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


@app.post(
    "/api/exchange-rate/refresh-async",
    status_code=202,
    tags=[TAG_EXCHANGE],
    summary="Iniciar actualizacion historica asincrona",
)
async def start_exchange_rate_refresh_async(background_tasks: BackgroundTasks):
    """Inicia la actualizacion historica de cotizaciones en segundo plano (202 Accepted)."""
    # Avoid parallel duplicate jobs
    existing = job_manager.find_running_job(ASYNC_JOB_TYPE_EXCHANGE_REFRESH)
    if existing:
        job = job_manager.get(existing)
        return JSONResponse(
            status_code=202,
            content={
                "job_id": existing,
                "status": job["status"],
                "message": "Job already running",
                "type": job["type"],
            },
        )

    job_id = job_manager.create_job(ASYNC_JOB_TYPE_EXCHANGE_REFRESH)
    background_tasks.add_task(_run_exchange_refresh_job, job_id)
    return {
        "job_id": job_id,
        "status": JobStatus.PENDING,
        "message": "Job accepted",
        "type": ASYNC_JOB_TYPE_EXCHANGE_REFRESH,
    }


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


@app.get(
    "/api/exchange-rate/refresh-status/{job_id}",
    tags=[TAG_EXCHANGE],
    summary="Alias estado refresh historico",
)
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
            age = (
                datetime.utcnow() - cached.get("updated_at", datetime.utcnow())
            ).total_seconds()
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
                data=cached["data"],
            ).dict()
        return ExchangeRateResponse(
            success=False,
            message="Could not retrieve current exchange rates",
            data=None,
        ).dict()

    except Exception as e:
        logger.error(f"Error getting current exchange rates: {e}")
        return ExchangeRateResponse(
            success=False, message=f"Internal error: {str(e)}", data=None
        ).dict()


@app.get(ENDPOINT_EXCHANGE_RATE_BY_DATE, tags=[TAG_EXCHANGE])
async def get_exchange_rates_by_date(
    date: date, currency: Optional[str] = None, db: Session = Depends(get_db)
):
    """Obtener cotizaciones por fecha especifica (busca fecha mas cercana si no existe)."""
    try:
        service = ExchangeRateService(db)
        exchange_rates = service.get_exchange_rate_by_date(date, currency)

        if exchange_rates:
            return ExchangeRateResponse(
                success=True,
                message=MSG_EXCHANGE_RATE_DATE_SUCCESS.format(date=date),
                data=[rate.dict() for rate in exchange_rates],
            ).dict()
        else:
            return ExchangeRateResponse(
                success=False, message=MSG_NO_EXCHANGE_RATE_DATE_DATA.format(date=date)
            ).dict()

    except Exception as e:
        logger.error(f"Error getting exchange rates by date {date}: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get(ENDPOINT_EXCHANGE_RATE_BY_DATE_CURRENCY, tags=[TAG_EXCHANGE])
async def get_exchange_rate_by_date_and_currency(
    date: date, currency: str, db: Session = Depends(get_db)
):
    """Obtener cotizacion especifica (fecha + moneda)."""
    try:
        if currency.upper() not in VALID_CURRENCY_CODES:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"Invalid currency code. Supported currencies: {', '.join(VALID_CURRENCY_CODES)}",
            )

        service = ExchangeRateService(db)
        exchange_rate = service.get_exchange_rate_closest_to_date(date, currency)

        if exchange_rate:
            return ExchangeRateResponse(
                success=True,
                message=f"Exchange rate for {currency.upper()} on {date} retrieved successfully",
                data=exchange_rate.dict(),
            ).dict()
        else:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f"No exchange rate data found for {currency.upper()} on {date} or previous dates",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error getting exchange rate by date {date} and currency {currency}: {e}"
        )
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
            age = (
                datetime.utcnow() - cached.get("updated_at", datetime.utcnow())
            ).total_seconds()
            if age > 55 * 60:
                need_update = True
        if force_refresh or need_update:
            _update_brou_cache()
            with _cache_lock:
                if brou_cache is None:  # mocked case
                    brou_cache = {
                        "data": [],
                        "updated_at": datetime.utcnow(),
                        "source": "BROU_SAMPLE",
                    }
                cached = brou_cache

        data_list = cached["data"] if cached else []
        source = cached.get("source", "BROU") if cached else "UNKNOWN"
        source_type = cached.get("source_type", "unknown") if cached else "unknown"

        if full:
            # Calcular edad de los datos
            data_age = None
            if cached and cached.get("updated_at"):
                data_age = (
                    datetime.utcnow() - cached["updated_at"]
                ).total_seconds() / 60  # en minutos

            # Información de estado para el frontend
            status_info = {
                "live": {
                    "label": "Datos en vivo",
                    "color": "green",
                    "description": "Cotizaciones obtenidas directamente del BROU",
                },
                "persisted": {
                    "label": "Datos históricos",
                    "color": "yellow",
                    "description": "Cotizaciones almacenadas de consultas anteriores",
                },
                "sample": {
                    "label": "Datos de muestra",
                    "color": "red",
                    "description": "Datos de ejemplo - API no disponible",
                },
            }

            current_status = status_info.get(
                source_type,
                {
                    "label": "Estado desconocido",
                    "color": "gray",
                    "description": "No se pudo determinar el estado de los datos",
                },
            )

            return {
                "success": True if data_list else False,
                "message": f"Cotizaciones BROU obtenidas ({len(data_list)} monedas)"
                if data_list
                else "Sin datos BROU",
                "data": data_list,
                "source": source,
                "source_type": source_type,
                "status": current_status,
                "timestamp": cached.get("updated_at").isoformat()
                if cached and cached.get("updated_at")
                else None,
                "data_age_minutes": round(data_age, 1)
                if data_age is not None
                else None,
                "is_fresh": data_age is not None
                and data_age < 60,  # Consideramos frescos datos de menos de 1 hora
                "frontend_display": {
                    "status_label": current_status["label"],
                    "status_color": current_status["color"],
                    "warning_message": current_status["description"]
                    if source_type in ["persisted", "sample"]
                    else None,
                },
            }
        return data_list
    except Exception as e:
        logger.error(f"Error getting current BROU rates: {e}")
        if full:
            return {
                "success": False,
                "message": f"Error interno: {str(e)}",
                "data": None,
            }
        return []


# =============================================================================
# METRICS ENDPOINTS
# =============================================================================


@app.get("/api/metrics", tags=["Sistema"])
async def get_comprehensive_metrics():
    """Obtener métricas completas del sistema (latencia, errores, estadísticas por endpoint)."""
    return await get_metrics()


@app.get("/api/metrics/health", tags=["Sistema"])
async def get_health_metrics():
    """Obtener estado de salud del sistema con métricas."""
    return await get_health()


# =============================================================================
# DASHBOARD ENDPOINTS
# =============================================================================


@app.get("/api/dashboard", tags=["Sistema"])
async def get_dashboard():
    """Obtener dashboard completo con métricas, alertas y estado del sistema."""
    return dashboard_service.get_dashboard_data()


@app.get("/api/dashboard/summary", tags=["Sistema"])
async def get_dashboard_summary():
    """Obtener resumen simplificado del dashboard para monitoreo rápido."""
    return dashboard_service.get_dashboard_summary()


# =============================================================================
# ALERTS ENDPOINTS
# =============================================================================


@app.get("/api/alerts", tags=["Sistema"])
async def get_alerts():
    """Obtener todas las alertas activas."""
    return {"alerts": alert_manager.get_active_alerts()}


@app.get("/api/alerts/all", tags=["Sistema"])
async def get_all_alerts(limit: int = 50):
    """Obtener todas las alertas (activas y resueltas)."""
    return {"alerts": alert_manager.get_all_alerts(limit)}


@app.get("/api/alerts/summary", tags=["Sistema"])
async def get_alerts_summary():
    """Obtener resumen estadístico de alertas."""
    return alert_manager.get_alert_summary()


@app.put("/api/alerts/{alert_id}/acknowledge", tags=["Sistema"])
async def acknowledge_alert(alert_id: str):
    """Marcar una alerta como reconocida."""
    success = alert_manager.acknowledge_alert(alert_id)
    if success:
        return {"message": f"Alert {alert_id} acknowledged"}
    raise HTTPException(status_code=404, detail="Alert not found")


@app.put("/api/alerts/{alert_id}/resolve", tags=["Sistema"])
async def resolve_alert(alert_id: str):
    """Resolver manualmente una alerta."""
    success = alert_manager.resolve_alert(alert_id)
    if success:
        return {"message": f"Alert {alert_id} resolved"}
    raise HTTPException(status_code=404, detail="Alert not found")


# =============================================================================
# PERFORMANCE BUDGET ENDPOINTS
# =============================================================================


@app.get("/api/performance/budgets", tags=["Sistema"])
async def get_performance_budgets():
    """Obtener todos los budgets de performance configurados."""
    try:
        if performance_budget_manager is None:
            # Return simple response when service is not available
            return {
                "budgets": {},
                "total_count": 0,
                "description": "Performance budgets not available - service temporarily disabled",
                "status": "service_unavailable",
            }

        # Try to get budgets with a reasonable timeout
        import asyncio

        try:
            budgets = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, performance_budget_manager.get_all_budgets
                ),
                timeout=15.0,  # Increased from 5.0 to 15.0 seconds
            )
            return {
                "budgets": budgets,
                "total_count": len(budgets),
                "description": "Performance budgets based on roadmap targets (Latency <200ms, Throughput >1000 req/min)",
            }
        except asyncio.TimeoutError:
            # If timeout, return simple response
            return {
                "budgets": {},
                "total_count": 0,
                "description": "Performance budgets request timed out - using fallback values",
                "status": "timeout_fallback",
            }
    except Exception as e:
        logger.error(f"Error getting performance budgets: {e}")
        return {
            "budgets": {},
            "total_count": 0,
            "description": "Error retrieving performance budgets",
            "error": str(e),
        }


@app.get("/api/performance/budgets/status", tags=["Sistema"])
async def get_performance_budgets_status():
    """Obtener estado actual de todos los budgets de performance."""
    try:
        if performance_budget_manager is None:
            # Return a simple response if performance budget manager is not available
            return {
                "budget_status": {},
                "timestamp": datetime.utcnow().isoformat(),
                "description": "Performance budget service not available",
                "message": "Performance monitoring is disabled",
            }

        # Try to get budget status with a longer timeout
        import asyncio

        try:
            # Create a task with longer timeout
            status = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, performance_budget_manager.get_budget_status
                ),
                timeout=30.0,  # Increased from 10.0 to 30.0 seconds
            )
            return {
                "budget_status": status,
                "timestamp": datetime.utcnow().isoformat(),
                "description": "Current performance budget status with health indicators",
            }
        except asyncio.TimeoutError:
            # If it times out, return a simple status with fallback values
            return {
                "budget_status": {
                    "timeout": {
                        "budget": "timeout",
                        "type": "system",
                        "target": 0,
                        "current": 0,
                        "warning_threshold": 0,
                        "critical_threshold": 0,
                        "status": "unknown",
                        "description": "Request timed out - using fallback values",
                    }
                },
                "timestamp": datetime.utcnow().isoformat(),
                "description": "Performance budget status request timed out",
                "message": "Using fallback values due to timeout",
            }
    except Exception as e:
        logger.error(f"Error getting performance budget status: {e}")
        return {
            "budget_status": {},
            "timestamp": datetime.utcnow().isoformat(),
            "description": "Error retrieving performance budget status",
            "error": str(e),
        }


@app.get("/api/performance/throughput", tags=["Sistema"])
async def get_throughput_metrics():
    """Obtener métricas de throughput actuales."""
    try:
        if performance_budget_manager is None:
            # Return simple response when service is not available
            return {
                "throughput": {
                    "requests_per_minute": 0,
                    "requests_per_hour": 0,
                    "peak_rpm": 0,
                    "current_window_requests": 0,
                    "window_start": datetime.utcnow().isoformat(),
                },
                "timestamp": datetime.utcnow().isoformat(),
                "description": "Throughput metrics not available - service temporarily disabled",
                "status": "service_unavailable",
            }

        # Try to get throughput metrics with a reasonable timeout
        import asyncio

        try:
            throughput = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: performance_budget_manager.get_throughput_metrics("global"),
                ),
                timeout=15.0,  # Increased from 5.0 to 15.0 seconds
            )
            # Enrich with simple application metrics for UI tiles
            try:
                simple = await get_simple_metrics()
            except Exception:
                simple = {}

            extended = dict(throughput)
            if isinstance(simple, dict):
                avg_ms = simple.get("avg_response_time_ms")
                err_pct = simple.get("error_rate_percent")
                uptime_sec = simple.get("uptime_seconds")
                # Availability proxy from error rate (100 - error%)
                availability_pct = None
                try:
                    availability_pct = (
                        max(0.0, 100.0 - float(err_pct))
                        if err_pct is not None
                        else None
                    )
                except Exception:
                    availability_pct = None

                if avg_ms is not None:
                    extended["avg_response_time_ms"] = avg_ms
                if err_pct is not None:
                    extended["error_rate_percent"] = err_pct
                if uptime_sec is not None:
                    extended["uptime_seconds"] = uptime_sec
                if availability_pct is not None:
                    extended["uptime_percent"] = availability_pct

            return {
                "throughput": extended,
                "timestamp": datetime.utcnow().isoformat(),
                "description": "Current request throughput metrics (requests per minute/hour)",
            }
        except asyncio.TimeoutError:
            # If timeout, return simple response
            return {
                "throughput": {
                    "requests_per_minute": 0,
                    "requests_per_hour": 0,
                    "peak_rpm": 0,
                    "current_window_requests": 0,
                    "window_start": datetime.utcnow().isoformat(),
                    "avg_response_time_ms": None,
                    "error_rate_percent": None,
                    "uptime_seconds": None,
                    "uptime_percent": None,
                },
                "timestamp": datetime.utcnow().isoformat(),
                "description": "Throughput metrics request timed out - using fallback values",
                "status": "timeout_fallback",
            }
    except Exception as e:
        logger.error(f"Error getting throughput metrics: {e}")
        return {
            "throughput": {
                "requests_per_minute": 0,
                "requests_per_hour": 0,
                "peak_rpm": 0,
                "current_window_requests": 0,
                "window_start": datetime.utcnow().isoformat(),
                "avg_response_time_ms": None,
                "error_rate_percent": None,
                "uptime_seconds": None,
                "uptime_percent": None,
            },
            "timestamp": datetime.utcnow().isoformat(),
            "description": "Error retrieving throughput metrics",
            "error": str(e),
        }


@app.post("/api/performance/enable-monitoring", tags=["Sistema"])
async def enable_performance_monitoring():
    """Habilitar monitoring y alertas de performance budgets."""
    global performance_budget_manager
    try:
        if performance_budget_manager is None:
            raise HTTPException(
                status_code=503, detail="Performance budget service not available"
            )

        # Re-initialize with monitoring and alerts enabled
        from performance_budget import get_performance_budget_manager

        performance_budget_manager = get_performance_budget_manager(
            enable_monitoring=True, enable_alerts=True
        )

        return {
            "message": "Performance monitoring and alerts enabled successfully",
            "status": "enabled",
            "budgets_count": len(performance_budget_manager.get_all_budgets()),
        }
    except Exception as e:
        logger.error(f"Error enabling performance monitoring: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error enabling performance monitoring: {str(e)}"
        )


@app.get("/api/performance/status", tags=["Sistema"])
async def get_performance_service_status():
    """Obtener estado del servicio de performance budgets."""
    try:
        if performance_budget_manager is None:
            return {
                "status": "unavailable",
                "message": "Performance budget service not initialized",
                "monitoring_enabled": False,
                "alerts_enabled": False,
            }

        # Check if monitoring is enabled by checking if the monitoring thread exists
        monitoring_enabled = (
            hasattr(performance_budget_manager, "_monitoring_thread")
            and performance_budget_manager._monitoring_thread.is_alive()
        )

        return {
            "status": "available",
            "message": "Performance budget service is running",
            "monitoring_enabled": monitoring_enabled,
            "alerts_enabled": True,  # We assume alerts are enabled if service is available
            "budgets_count": len(performance_budget_manager.get_all_budgets()),
        }
    except Exception as e:
        logger.error(f"Error getting performance service status: {e}")
        return {
            "status": "error",
            "message": f"Error checking service status: {str(e)}",
            "monitoring_enabled": False,
            "alerts_enabled": False,
        }


# =============================================================================
# ADVANCED HEALTH CHECK ENDPOINTS
# =============================================================================


@app.get("/api/health/advanced", tags=["Sistema"])
async def get_advanced_health_endpoint(force_refresh: bool = False):
    """Obtener health check avanzado completo del sistema.

    Incluye verificación de:
    - Base de datos (conectividad y estadísticas)
    - APIs externas (BROU, BCU)
    - Recursos del sistema (CPU, memoria, disco)
    - Métricas de aplicación (latencia, errores)

    Parámetros:
    - force_refresh: bool = False - Forzar actualización de caché (por defecto usa caché de 30s)
    """
    return await get_advanced_health(force_refresh=force_refresh)


@app.get("/api/health/simple", tags=["Sistema"])
async def get_simple_health_endpoint():
    """Obtener health check simple para load balancers.

    Retorna estado simple (OK/FAIL) con conteo de issues para monitoreo básico.
    """
    return await get_simple_health()


# =============================================================================
# CIRCUIT BREAKER ENDPOINTS
# =============================================================================


@app.get("/api/circuit-breakers", tags=["Sistema"])
async def get_circuit_breakers_status():
    """Obtener estado de todos los circuit breakers."""
    try:
        all_cb = get_all_circuit_breakers()
        status = {}

        for name, cb in all_cb.items():
            cb_status = get_circuit_breaker_status(name)
            if cb_status:
                status[name] = cb_status

        return {
            "circuit_breakers": status,
            "total_count": len(status),
            "open_count": sum(1 for cb in status.values() if cb["state"] == "open"),
            "half_open_count": sum(
                1 for cb in status.values() if cb["state"] == "half_open"
            ),
            "closed_count": sum(1 for cb in status.values() if cb["state"] == "closed"),
        }

    except Exception as e:
        logger.error(f"Error getting circuit breaker status: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving circuit breaker status: {str(e)}"
        )


@app.get("/api/circuit-breakers/{name}", tags=["Sistema"])
async def get_circuit_breaker_status_endpoint(name: str):
    """Obtener estado de un circuit breaker específico."""
    try:
        status = get_circuit_breaker_status(name)
        if status is None:
            raise HTTPException(
                status_code=404, detail=f"Circuit breaker '{name}' not found"
            )

        return status

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting circuit breaker status for {name}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving circuit breaker status: {str(e)}"
        )


@app.post("/api/circuit-breakers/{name}/reset", tags=["Sistema"])
async def reset_circuit_breaker_endpoint(name: str):
    """Resetear un circuit breaker a estado cerrado."""
    try:
        success = reset_circuit_breaker(name)
        if not success:
            raise HTTPException(
                status_code=404, detail=f"Circuit breaker '{name}' not found"
            )

        logger.info(f"Circuit breaker '{name}' reset by API call")
        return {
            "message": f"Circuit breaker '{name}' has been reset to closed state",
            "circuit_breaker": name,
            "action": "reset",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting circuit breaker {name}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error resetting circuit breaker: {str(e)}"
        )


# -----------------------------------------------------------------------------
# __main__ entrypoint (used only for local development / test coverage)
# -----------------------------------------------------------------------------
if __name__ == "__main__":  # pragma: no cover (explicitly exercised in tests)
    import uvicorn  # local import to avoid mandatory dependency at import time

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
