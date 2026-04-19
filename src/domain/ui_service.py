from datetime import date
from typing import List, Optional
import logging

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.domain.models import UIValue
from src.infrastructure.database import UIRecord

logger = logging.getLogger(__name__)


class UIService:
    def __init__(self, db: Session):
        self.db = db

    def get_ui_by_date(self, date: date) -> Optional[UIValue]:
        """Get UI value for a specific date."""
        try:
            record = self.db.query(UIRecord).filter(UIRecord.date == date).first()

            if record:
                return UIValue(date=record.date, value=record.value)
            return None

        except Exception as e:
            logger.error(f"Error getting UI by date {date}: {e}")
            return None

    def get_ui_by_date_range(self, start_date: date, end_date: date) -> List[UIValue]:
        """Get UI values for a date range."""
        try:
            records = (
                self.db.query(UIRecord)
                .filter(and_(UIRecord.date >= start_date, UIRecord.date <= end_date))
                .order_by(UIRecord.date)
                .all()
            )

            return [UIValue(date=record.date, value=record.value) for record in records]

        except Exception as e:
            logger.error(f"Error getting UI by range {start_date} - {end_date}: {e}")
            return []

    def get_latest_ui(self) -> Optional[UIValue]:
        """Get the most recent UI value."""
        try:
            record = self.db.query(UIRecord).order_by(UIRecord.date.desc()).first()

            if record:
                return UIValue(date=record.date, value=record.value)
            return None

        except Exception as e:
            logger.error(f"Error getting latest UI: {e}")
            return None

    def get_ui_closest_to_date(self, target_date: date) -> Optional[UIValue]:
        """Get UI value closest to a date (useful for non-working days)."""
        try:
            exact_record = (
                self.db.query(UIRecord).filter(UIRecord.date == target_date).first()
            )
            if exact_record:
                return UIValue(date=exact_record.date, value=exact_record.value)

            closest_record = (
                self.db.query(UIRecord)
                .filter(UIRecord.date <= target_date)
                .order_by(UIRecord.date.desc())
                .first()
            )

            if closest_record:
                return UIValue(date=closest_record.date, value=closest_record.value)
            return None

        except Exception as e:
            logger.error(f"Error getting UI closest to {target_date}: {e}")
            return None

    def get_total_records(self) -> int:
        """Get total number of records in database."""
        try:
            return self.db.query(UIRecord).count()
        except Exception as e:
            logger.error(f"Error counting records: {e}")
            return 0

    def get_date_range_available(self) -> tuple[Optional[date], Optional[date]]:
        """Get available date range in database."""
        try:
            min_date = self.db.query(UIRecord.date).order_by(UIRecord.date.asc()).first()
            max_date = self.db.query(UIRecord.date).order_by(UIRecord.date.desc()).first()

            return (
                min_date[0] if min_date else None,
                max_date[0] if max_date else None,
            )

        except Exception as e:
            logger.error(f"Error getting date range: {e}")
            return None, None

    def purge_future_records(self, ref_date: date | None = None) -> int:
        """Eliminar registros UI con fecha futura (sanidad de datos)."""
        try:
            ref = ref_date or date.today()
            q = self.db.query(UIRecord).filter(UIRecord.date > ref)
            count = q.count()
            if count:
                q.delete(synchronize_session=False)
                self.db.commit()
                logger.warning(
                    f"Purged {count} future UI records (> {ref.isoformat()})"
                )
            return count
        except Exception as e:  # noqa: BLE001
            logger.error(f"Error purging future UI records: {e}")
            self.db.rollback()
            return 0
