"""Exchange Rate router endpoints."""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import date, datetime
import logging
from typing import Optional

from src.infrastructure.database import get_db, SessionLocal
from src.domain.models import ExchangeRateResponse
from src.domain.services import ExchangeRateService
from src.domain.excel_processor import ExchangeRateExcelProcessor
from src.application.security_utils import InputValidator
from src.utils.constants import (
    TAG_EXCHANGE,
    ENDPOINT_EXCHANGE_RATE_LATEST,
    ENDPOINT_EXCHANGE_RATE_INFO,
    ENDPOINT_EXCHANGE_RATE_BY_CURRENCY,
    ENDPOINT_EXCHANGE_RATE_RANGE,
    ENDPOINT_EXCHANGE_RATE_REFRESH,
    ENDPOINT_EXCHANGE_RATE_BY_DATE,
    VALID_CURRENCY_CODES,
    MSG_LATEST_EXCHANGE_RATE_SUCCESS,
    MSG_NO_EXCHANGE_RATE_DATA,
    MSG_EXCHANGE_RATE_CURRENCY_SUCCESS,
    MSG_NO_EXCHANGE_RATE_CURRENCY_DATA,
    MSG_EXCHANGE_RATE_RANGE_SUCCESS,
    MSG_EXCHANGE_RATE_DATE_SUCCESS,
    MSG_NO_EXCHANGE_RATE_DATE_DATA,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=[TAG_EXCHANGE])

# Global exchange processor instance and job manager (shared from main.py)
exchange_rate_excel_processor: ExchangeRateExcelProcessor | None = None
job_manager = None
bcu_cache = None
_cache_lock = None

# Job type constants
ASYNC_JOB_TYPE_EXCHANGE_REFRESH = "exchange_rate_refresh"


def set_exchange_rate_processor(processor: ExchangeRateExcelProcessor):
    """Set the shared exchange processor instance."""
    global exchange_rate_excel_processor
    exchange_rate_excel_processor = processor


def set_job_manager(jm):
    """Set the job manager instance."""
    global job_manager
    job_manager = jm


def set_cache_and_lock(cache, lock):
    """Set the cache and lock instances."""
    global bcu_cache, _cache_lock
    bcu_cache = cache
    _cache_lock = lock


@router.get(ENDPOINT_EXCHANGE_RATE_LATEST)
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


@router.get(ENDPOINT_EXCHANGE_RATE_INFO)
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


@router.get(ENDPOINT_EXCHANGE_RATE_BY_CURRENCY)
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


@router.get(ENDPOINT_EXCHANGE_RATE_RANGE)
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


# Note: /api/exchange-rate/current is defined in main.py BEFORE including this router
# to ensure it takes precedence over the dynamic /api/exchange-rate/{date} route


@router.get(ENDPOINT_EXCHANGE_RATE_BY_DATE)
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


@router.post(ENDPOINT_EXCHANGE_RATE_REFRESH)
async def refresh_exchange_rate_historical_data(db: Session = Depends(get_db)):
    """Actualizar datos historicos de cotizaciones (INE)."""
    try:
        logger.info(
            "Starting historical exchange rate data update from INE (synchronous endpoint)..."
        )
        if not exchange_rate_excel_processor:
            raise RuntimeError("Exchange rate processor not initialized")

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


def _run_exchange_refresh_job(job_id: str):  # runs in background thread
    """Internal function executed in background to perform the heavy refresh and update job metadata."""
    if not job_manager:
        logger.error(f"[Job {job_id}] Job manager not initialized")
        return

    job_manager.mark_running(job_id)
    # New DB session (cannot reuse dependency outside request context)
    db_local = SessionLocal()
    try:
        logger.info(f"[Job {job_id}] Running exchange historical refresh")
        if not exchange_rate_excel_processor:
            raise RuntimeError("Exchange processor not initialized")

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


@router.post(
    "/api/exchange-rate/refresh-async",
    status_code=202,
    summary="Iniciar actualizacion historica asincrona",
)
async def start_exchange_rate_refresh_async(background_tasks: BackgroundTasks):
    """Inicia la actualizacion historica de cotizaciones en segundo plano (202 Accepted)."""
    if not job_manager:
        raise HTTPException(status_code=500, detail="Job manager not initialized")

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
        "status": "pending",
        "message": "Job accepted",
        "type": ASYNC_JOB_TYPE_EXCHANGE_REFRESH,
    }


@router.get("/api/jobs/{job_id}", summary="Estado de un job")
async def get_job_status(job_id: str):
    if not job_manager:
        raise HTTPException(status_code=500, detail="Job manager not initialized")

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


@router.get("/api/jobs", summary="Listado de jobs (debug)")
async def list_jobs():
    if not job_manager:
        raise HTTPException(status_code=500, detail="Job manager not initialized")

    # WARNING: In-memory only; suitable for development/testing
    ids = []
    # Access internal structure safely
    for job_id in list(job_manager._jobs.keys()):  # type: ignore[attr-defined]
        job = job_manager.get(job_id)
        if job:
            ids.append({"job_id": job_id, "type": job["type"], "status": job["status"]})
    return {"jobs": ids}


@router.get(
    "/api/exchange-rate/refresh-status/{job_id}",
    summary="Alias estado refresh historico",
)
async def get_exchange_refresh_status(job_id: str):
    return await get_job_status(job_id)
