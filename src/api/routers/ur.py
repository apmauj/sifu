"""UR (Unidad Reajustable) router endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import logging
from datetime import datetime as _dt

from src.api.error_handling import log_and_raise_http_exception
from src.infrastructure.database import get_db
from src.domain.models import URResponse, RefreshResponse
from src.domain.services import URService
from src.domain.excel_processor import URExcelProcessor
from src.domain.pydantic_models import URRangeRequestModel
from src.application.security_utils import SecurityValidator, InputValidator
from src.utils.constants import (
    TAG_UR,
    MSG_LATEST_UR_SUCCESS,
    MSG_NO_UR_DATA,
    MSG_UR_YEAR_MONTH_SUCCESS,
    MSG_NO_UR_YEAR_MONTH_DATA,
    MSG_UR_YEAR_SUCCESS,
    MSG_NO_UR_YEAR_DATA,
    MSG_INVALID_MONTH,
    MSG_INVALID_PERIOD_RANGE,
    MSG_UR_RANGE_SUCCESS,
    MSG_NO_UR_RANGE_DATA,
    MSG_UR_PENDING_CURRENT_MONTH,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ur", tags=[TAG_UR])

# Global UR excel processor instance (shared from main.py)
ur_excel_processor: URExcelProcessor | None = None


def set_ur_excel_processor(processor: URExcelProcessor):
    """Set the shared UR excel processor instance."""
    global ur_excel_processor
    ur_excel_processor = processor


@router.get("/latest")
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
        log_and_raise_http_exception(
            logger=logger,
            status_code=500,
            log_message="Error in get_latest_ur",
            error=e,
            detail="Internal server error",
        )


@router.get("/year-month/{year}/{month}")
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
        log_and_raise_http_exception(
            logger=logger,
            status_code=500,
            log_message="Error in get_ur_by_year_month",
            error=e,
            detail="Internal server error",
        )


@router.get("/year/{year}")
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
        log_and_raise_http_exception(
            logger=logger,
            status_code=500,
            log_message="Error in get_ur_by_year",
            error=e,
            detail="Internal server error",
        )


@router.get("/range/{start_year}/{start_month}/{end_year}/{end_month}")
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
                message=MSG_INVALID_MONTH,
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
        log_and_raise_http_exception(
            logger=logger,
            status_code=500,
            log_message="Error in get_ur_by_range",
            error=e,
            detail="Internal server error",
        )


@router.post("/range")
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


@router.post("/refresh")
async def refresh_ur_data(db: Session = Depends(get_db)):
    """Actualizar datos de UR desde BHU (descarga + procesamiento)."""
    try:
        logger.info("Starting UR data update...")

        if not ur_excel_processor:
            raise RuntimeError("UR Excel processor not initialized")

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
        log_and_raise_http_exception(
            logger=logger,
            status_code=500,
            log_message="Error in refresh_ur_data",
            error=e,
            detail="Internal server error",
        )


@router.get("/info")
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
                now = _dt.utcnow()
                if (latest_ur.year, latest_ur.month) < (now.year, now.month):
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
        log_and_raise_http_exception(
            logger=logger,
            status_code=500,
            log_message="Error in get_ur_info",
            error=e,
            detail="Internal server error",
        )
