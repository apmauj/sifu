"""UI (Unidad Indexada) router endpoints."""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import date
import logging

from src.infrastructure.database import get_db
from src.domain.models import UIResponse, RefreshResponse
from src.domain.services import UIService
from src.domain.excel_processor import ExcelProcessor
from src.utils.constants import (
    TAG_UI,
    MSG_LATEST_UI_SUCCESS,
    MSG_NO_UI_DATA,
    MSG_UI_DATE_SUCCESS,
    MSG_UI_RANGE_SUCCESS,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ui", tags=[TAG_UI])

# Global excel processor instance (shared from main.py)
excel_processor: ExcelProcessor | None = None


def set_excel_processor(processor: ExcelProcessor):
    """Set the shared excel processor instance."""
    global excel_processor
    excel_processor = processor


@router.get("/latest")
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


@router.get("/{date}")
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


@router.get("/range/{start_date}/{end_date}")
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


@router.post("/refresh")
async def refresh_data(
    background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """Actualizar datos de UI desde INE (descarga y procesamiento)."""
    try:
        if not excel_processor:
            raise RuntimeError("Excel processor not initialized")

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
