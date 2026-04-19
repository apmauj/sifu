from typing import List, Optional
import logging

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from src.domain.models import URValue
from src.infrastructure.database import URRecord

logger = logging.getLogger(__name__)


class URService:
    def __init__(self, db: Session):
        self.db = db

    def get_ur_by_year_month(self, year: int, month: int) -> Optional[URValue]:
        """Get UR value for a specific year and month."""
        try:
            record = (
                self.db.query(URRecord)
                .filter(URRecord.year == year, URRecord.month == month)
                .first()
            )

            if record:
                return URValue(year=record.year, month=record.month, value=record.value)
            return None

        except Exception as e:
            logger.error(f"Error getting UR by year-month {year}-{month}: {e}")
            return None

    def get_ur_by_year(self, year: int) -> List[URValue]:
        """Get all UR values for a specific year."""
        try:
            records = (
                self.db.query(URRecord)
                .filter(URRecord.year == year)
                .order_by(URRecord.month)
                .all()
            )

            return [
                URValue(year=record.year, month=record.month, value=record.value)
                for record in records
            ]

        except Exception as e:
            logger.error(f"Error getting UR by year {year}: {e}")
            return []

    def get_ur_by_range(
        self, start_year: int, start_month: int, end_year: int, end_month: int
    ) -> List[URValue]:
        """Get UR values for a range of years and months."""
        try:
            conditions = []

            if start_year == end_year:
                conditions.append(
                    and_(
                        URRecord.year == start_year,
                        URRecord.month >= start_month,
                        URRecord.month <= end_month,
                    )
                )
            else:
                conditions.append(
                    and_(URRecord.year == start_year, URRecord.month >= start_month)
                )

                if end_year - start_year > 1:
                    conditions.append(
                        and_(URRecord.year > start_year, URRecord.year < end_year)
                    )

                conditions.append(
                    and_(URRecord.year == end_year, URRecord.month <= end_month)
                )

            records = (
                self.db.query(URRecord)
                .filter(or_(*conditions))
                .order_by(URRecord.year, URRecord.month)
                .all()
            )

            return [
                URValue(year=record.year, month=record.month, value=record.value)
                for record in records
            ]

        except Exception as e:
            logger.error(
                f"Error getting UR by range {start_year}-{start_month} to {end_year}-{end_month}: {e}"
            )
            return []

    def get_latest_ur(self) -> Optional[URValue]:
        """Get the most recent UR value."""
        try:
            record = (
                self.db.query(URRecord)
                .order_by(URRecord.year.desc(), URRecord.month.desc())
                .first()
            )

            if record:
                return URValue(year=record.year, month=record.month, value=record.value)
            return None

        except Exception as e:
            logger.error(f"Error getting latest UR: {e}")
            return None

    def get_total_records(self) -> int:
        """Get total number of UR records in database."""
        try:
            return self.db.query(URRecord).count()
        except Exception as e:
            logger.error(f"Error counting UR records: {e}")
            return 0

    def get_year_range_available(self) -> tuple[Optional[int], Optional[int]]:
        """Get available year range in database."""
        try:
            min_year = self.db.query(URRecord.year).order_by(URRecord.year.asc()).first()
            max_year = self.db.query(URRecord.year).order_by(URRecord.year.desc()).first()

            return (
                min_year[0] if min_year else None,
                max_year[0] if max_year else None,
            )

        except Exception as e:
            logger.error(f"Error getting year range: {e}")
            return None, None

    def get_available_years(self) -> List[int]:
        """Get list of available years."""
        try:
            years = (
                self.db.query(URRecord.year)
                .distinct()
                .order_by(URRecord.year.desc())
                .all()
            )
            return [year[0] for year in years]
        except Exception as e:
            logger.error(f"Error getting available years: {e}")
            return []
