from src.infrastructure.database import UIRecord, URRecord, ExchangeRateRecord, SessionLocal
from src.domain.exchange_rate_service import ExchangeRateService
from src.domain.ui_service import UIService
from src.domain.ur_service import URService
import logging

logger = logging.getLogger(__name__)

__all__ = [
    "UIService",
    "URService",
    "ExchangeRateService",
    "get_ui_table_record_count",
    "get_ur_table_record_count",
    "get_exchange_rate_table_record_count",
]


# Helper functions used by bootstrap logic for lightweight table population checks
def get_ui_table_record_count() -> int:
    db = SessionLocal()
    try:
        return db.query(UIRecord).count()
    except Exception as e:  # noqa: BLE001
        logger.error(f"Error counting UI records: {e}")
        return 0
    finally:
        db.close()


def get_ur_table_record_count() -> int:
    db = SessionLocal()
    try:
        return db.query(URRecord).count()
    except Exception as e:  # noqa: BLE001
        logger.error(f"Error counting UR records: {e}")
        return 0
    finally:
        db.close()


def get_exchange_rate_table_record_count() -> int:
    db = SessionLocal()
    try:
        return db.query(ExchangeRateRecord).count()
    except Exception as e:  # noqa: BLE001
        logger.error(f"Error counting ExchangeRate records: {e}")
        return 0
    finally:
        db.close()


