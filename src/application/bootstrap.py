"""Bootstrap logic for initial dataset population.

Detects empty tables (UI, UR, ExchangeRate) and performs initial load.
Returns a structured summary for logging and tests.
"""

from __future__ import annotations

from typing import Dict, Any
import logging
from src.infrastructure.database import SessionLocal
from src.domain.excel_processor import (
    ExcelProcessor,
    URExcelProcessor,
    ExchangeRateExcelProcessor,
)
from src.domain.services import (
    get_ui_table_record_count,
    get_ur_table_record_count,
    get_exchange_rate_table_record_count,
)

logger = logging.getLogger(__name__)


def perform_bootstrap(
    force: bool = False,
    excel_processor: ExcelProcessor | None = None,
    ur_excel_processor: URExcelProcessor | None = None,
    exchange_rate_excel_processor: ExchangeRateExcelProcessor | None = None,
) -> Dict[str, Any]:
    """Perform initial data population if tables are empty (or force=True).

    Returns dict with per-section status for observability/testing.
    """
    excel_processor = excel_processor or ExcelProcessor()
    ur_excel_processor = ur_excel_processor or URExcelProcessor()
    exchange_rate_excel_processor = (
        exchange_rate_excel_processor or ExchangeRateExcelProcessor()
    )

    summary: Dict[str, Any] = {"ui": {}, "ur": {}, "exchange": {}}

    # UI
    try:
        ui_count = get_ui_table_record_count()
        if ui_count == 0 or force:
            logger.info("[Bootstrap] UI: loading (count=%s force=%s)", ui_count, force)
            db = SessionLocal()
            try:
                success, message, processed = excel_processor.refresh_data(db)
                summary["ui"] = {
                    "attempted": True,
                    "success": success,
                    "message": message,
                    "processed": processed,
                }
            finally:
                db.close()
        else:
            summary["ui"] = {
                "attempted": False,
                "success": True,
                "message": "present",
                "count": ui_count,
            }
    except Exception as e:  # noqa: BLE001
        logger.error("[Bootstrap] UI failure: %s", e)
        summary["ui"] = {"attempted": True, "success": False, "error": str(e)}

    # UR
    try:
        ur_count = get_ur_table_record_count()
        if ur_count == 0 or force:
            logger.info("[Bootstrap] UR: loading (count=%s force=%s)", ur_count, force)
            db = SessionLocal()
            try:
                success, message, processed = ur_excel_processor.refresh_data(db)
                summary["ur"] = {
                    "attempted": True,
                    "success": success,
                    "message": message,
                    "processed": processed,
                }
            finally:
                db.close()
        else:
            summary["ur"] = {
                "attempted": False,
                "success": True,
                "message": "present",
                "count": ur_count,
            }
    except Exception as e:  # noqa: BLE001
        logger.error("[Bootstrap] UR failure: %s", e)
        summary["ur"] = {"attempted": True, "success": False, "error": str(e)}

    # Exchange Rate
    try:
        exch_count = get_exchange_rate_table_record_count()
        if exch_count == 0 or force:
            logger.info(
                "[Bootstrap] ExchangeRate: loading (count=%s force=%s)",
                exch_count,
                force,
            )
            db = SessionLocal()
            try:
                success, message, processed = (
                    exchange_rate_excel_processor.refresh_data(db)
                )
                summary["exchange"] = {
                    "attempted": True,
                    "success": success,
                    "message": message,
                    "processed": processed,
                }
            finally:
                db.close()
        else:
            summary["exchange"] = {
                "attempted": False,
                "success": True,
                "message": "present",
                "count": exch_count,
            }
    except Exception as e:  # noqa: BLE001
        logger.error("[Bootstrap] Exchange failure: %s", e)
        summary["exchange"] = {"attempted": True, "success": False, "error": str(e)}

    return summary

