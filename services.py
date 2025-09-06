from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from database import UIRecord, URRecord, ExchangeRateRecord, SessionLocal
from models import UIValue, URValue, ExchangeRateValue
import logging

logger = logging.getLogger(__name__)


class UIService:
    def __init__(self, db: Session):
        self.db = db

    def get_ui_by_date(self, date: date) -> Optional[UIValue]:
        """Get UI value for a specific date"""
        try:
            record = self.db.query(UIRecord).filter(UIRecord.date == date).first()

            if record:
                return UIValue(date=record.date, value=record.value)
            else:
                return None

        except Exception as e:
            logger.error(f"Error getting UI by date {date}: {e}")
            return None

    def get_ui_by_date_range(self, start_date: date, end_date: date) -> List[UIValue]:
        """Get UI values for a date range"""
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
        """Get the most recent UI value"""
        try:
            record = self.db.query(UIRecord).order_by(UIRecord.date.desc()).first()

            if record:
                return UIValue(date=record.date, value=record.value)
            else:
                return None

        except Exception as e:
            logger.error(f"Error getting latest UI: {e}")
            return None

    def get_ui_closest_to_date(self, target_date: date) -> Optional[UIValue]:
        """Get UI value closest to a date (useful for non-working days)"""
        try:
            # Search for exact date first
            exact_record = (
                self.db.query(UIRecord).filter(UIRecord.date == target_date).first()
            )
            if exact_record:
                return UIValue(date=exact_record.date, value=exact_record.value)

            # If not found, search for closest previous date
            closest_record = (
                self.db.query(UIRecord)
                .filter(UIRecord.date <= target_date)
                .order_by(UIRecord.date.desc())
                .first()
            )

            if closest_record:
                return UIValue(date=closest_record.date, value=closest_record.value)
            else:
                return None

        except Exception as e:
            logger.error(f"Error getting UI closest to {target_date}: {e}")
            return None

    def get_total_records(self) -> int:
        """Get total number of records in database"""
        try:
            return self.db.query(UIRecord).count()
        except Exception as e:
            logger.error(f"Error counting records: {e}")
            return 0

    def get_date_range_available(self) -> tuple[Optional[date], Optional[date]]:
        """Get available date range in database"""
        try:
            min_date = (
                self.db.query(UIRecord.date).order_by(UIRecord.date.asc()).first()
            )
            max_date = (
                self.db.query(UIRecord.date).order_by(UIRecord.date.desc()).first()
            )

            return (
                min_date[0] if min_date else None,
                max_date[0] if max_date else None,
            )

        except Exception as e:
            logger.error(f"Error getting date range: {e}")
            return None, None


class URService:
    def __init__(self, db: Session):
        self.db = db

    def get_ur_by_year_month(self, year: int, month: int) -> Optional[URValue]:
        """Get UR value for a specific year and month"""
        try:
            record = (
                self.db.query(URRecord)
                .filter(URRecord.year == year, URRecord.month == month)
                .first()
            )

            if record:
                return URValue(year=record.year, month=record.month, value=record.value)
            else:
                return None

        except Exception as e:
            logger.error(f"Error getting UR by year-month {year}-{month}: {e}")
            return None

    def get_ur_by_year(self, year: int) -> List[URValue]:
        """Get all UR values for a specific year"""
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
        """Get UR values for a range of years and months"""
        try:
            # Create conditions for the range
            conditions = []

            if start_year == end_year:
                # Same year, filter by months
                conditions.append(
                    and_(
                        URRecord.year == start_year,
                        URRecord.month >= start_month,
                        URRecord.month <= end_month,
                    )
                )
            else:
                # Different years
                # Start year: from start_month to December
                conditions.append(
                    and_(URRecord.year == start_year, URRecord.month >= start_month)
                )

                # Intermediate years: all months
                if end_year - start_year > 1:
                    conditions.append(
                        and_(URRecord.year > start_year, URRecord.year < end_year)
                    )

                # End year: from January to end_month
                conditions.append(
                    and_(URRecord.year == end_year, URRecord.month <= end_month)
                )

            # Combine conditions with OR
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
        """Get the most recent UR value"""
        try:
            record = (
                self.db.query(URRecord)
                .order_by(URRecord.year.desc(), URRecord.month.desc())
                .first()
            )

            if record:
                return URValue(year=record.year, month=record.month, value=record.value)
            else:
                return None

        except Exception as e:
            logger.error(f"Error getting latest UR: {e}")
            return None

    def get_total_records(self) -> int:
        """Get total number of UR records in database"""
        try:
            return self.db.query(URRecord).count()
        except Exception as e:
            logger.error(f"Error counting UR records: {e}")
            return 0

    def get_year_range_available(self) -> tuple[Optional[int], Optional[int]]:
        """Get available year range in database"""
        try:
            min_year = (
                self.db.query(URRecord.year).order_by(URRecord.year.asc()).first()
            )
            max_year = (
                self.db.query(URRecord.year).order_by(URRecord.year.desc()).first()
            )

            return (
                min_year[0] if min_year else None,
                max_year[0] if max_year else None,
            )

        except Exception as e:
            logger.error(f"Error getting year range: {e}")
            return None, None

    def get_available_years(self) -> List[int]:
        """Get list of available years"""
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


class ExchangeRateService:
    def __init__(self, db: Session):
        self.db = db

    def get_exchange_rate_by_date(
        self, date: date, currency: Optional[str] = None
    ) -> List[ExchangeRateValue]:
        """Get exchange rates for a specific date, optionally filtered by currency"""
        try:
            query = self.db.query(ExchangeRateRecord).filter(
                ExchangeRateRecord.date == date
            )

            if currency:
                query = query.filter(ExchangeRateRecord.currency == currency.upper())

            records = query.order_by(ExchangeRateRecord.currency).all()

            return [
                ExchangeRateValue(
                    date=record.date,
                    currency=record.currency,
                    buy_rate=record.buy_rate,
                    sell_rate=record.sell_rate,
                    average_rate=record.average_rate,
                    arbitrage=record.arbitrage,
                )
                for record in records
            ]

        except Exception as e:
            logger.error(f"Error getting exchange rates by date {date}: {e}")
            return []

    def get_exchange_rate_by_currency(
        self, currency: str, limit: int = 30
    ) -> List[ExchangeRateValue]:
        """Get recent exchange rates for a specific currency"""
        try:
            records = (
                self.db.query(ExchangeRateRecord)
                .filter(ExchangeRateRecord.currency == currency.upper())
                .order_by(ExchangeRateRecord.date.desc())
                .limit(limit)
                .all()
            )

            return [
                ExchangeRateValue(
                    date=record.date,
                    currency=record.currency,
                    buy_rate=record.buy_rate,
                    sell_rate=record.sell_rate,
                    average_rate=record.average_rate,
                    arbitrage=record.arbitrage,
                )
                for record in records
            ]

        except Exception as e:
            logger.error(f"Error getting exchange rates by currency {currency}: {e}")
            return []

    def get_exchange_rate_by_date_range(
        self, start_date: date, end_date: date, currency: Optional[str] = None
    ) -> List[ExchangeRateValue]:
        """Get exchange rates for a date range, optionally filtered by currency"""
        try:
            query = self.db.query(ExchangeRateRecord).filter(
                and_(
                    ExchangeRateRecord.date >= start_date,
                    ExchangeRateRecord.date <= end_date,
                )
            )

            if currency:
                query = query.filter(ExchangeRateRecord.currency == currency.upper())

            records = query.order_by(
                ExchangeRateRecord.date, ExchangeRateRecord.currency
            ).all()

            return [
                ExchangeRateValue(
                    date=record.date,
                    currency=record.currency,
                    buy_rate=record.buy_rate,
                    sell_rate=record.sell_rate,
                    average_rate=record.average_rate,
                    arbitrage=record.arbitrage,
                )
                for record in records
            ]

        except Exception as e:
            logger.error(
                f"Error getting exchange rates by range {start_date} - {end_date}: {e}"
            )
            return []

    def get_latest_exchange_rates(
        self, currencies: Optional[List[str]] = None
    ) -> List[ExchangeRateValue]:
        """Get the most recent exchange rates for all or specified currencies"""
        try:
            # Get the latest date
            latest_date_query = (
                self.db.query(ExchangeRateRecord.date)
                .order_by(ExchangeRateRecord.date.desc())
                .first()
            )

            if not latest_date_query:
                return []

            latest_date = latest_date_query[0]

            # Get all records for the latest date
            query = self.db.query(ExchangeRateRecord).filter(
                ExchangeRateRecord.date == latest_date
            )

            if currencies:
                upper_currencies = [c.upper() for c in currencies]
                query = query.filter(ExchangeRateRecord.currency.in_(upper_currencies))

            records = query.order_by(ExchangeRateRecord.currency).all()

            return [
                ExchangeRateValue(
                    date=record.date,
                    currency=record.currency,
                    buy_rate=record.buy_rate,
                    sell_rate=record.sell_rate,
                    average_rate=record.average_rate,
                    arbitrage=record.arbitrage,
                )
                for record in records
            ]

        except Exception as e:
            logger.error(f"Error getting latest exchange rates: {e}")
            return []

    def get_exchange_rate_closest_to_date(
        self, target_date: date, currency: str
    ) -> Optional[ExchangeRateValue]:
        """Get exchange rate closest to a date for a specific currency"""
        try:
            # Search for exact date first
            exact_record = (
                self.db.query(ExchangeRateRecord)
                .filter(
                    and_(
                        ExchangeRateRecord.date == target_date,
                        ExchangeRateRecord.currency == currency.upper(),
                    )
                )
                .first()
            )

            if exact_record:
                return ExchangeRateValue(
                    date=exact_record.date,
                    currency=exact_record.currency,
                    buy_rate=exact_record.buy_rate,
                    sell_rate=exact_record.sell_rate,
                    average_rate=exact_record.average_rate,
                    arbitrage=exact_record.arbitrage,
                )

            # If not found, search for closest previous date
            closest_record = (
                self.db.query(ExchangeRateRecord)
                .filter(
                    and_(
                        ExchangeRateRecord.date <= target_date,
                        ExchangeRateRecord.currency == currency.upper(),
                    )
                )
                .order_by(ExchangeRateRecord.date.desc())
                .first()
            )

            if closest_record:
                return ExchangeRateValue(
                    date=closest_record.date,
                    currency=closest_record.currency,
                    buy_rate=closest_record.buy_rate,
                    sell_rate=closest_record.sell_rate,
                    average_rate=closest_record.average_rate,
                    arbitrage=closest_record.arbitrage,
                )
            else:
                return None

        except Exception as e:
            logger.error(
                f"Error getting exchange rate closest to {target_date} for {currency}: {e}"
            )
            return None

    def get_total_records(self) -> int:
        """Get total number of exchange rate records in database"""
        try:
            return self.db.query(ExchangeRateRecord).count()
        except Exception as e:
            logger.error(f"Error counting exchange rate records: {e}")
            return 0

    def get_date_range_available(self) -> tuple[Optional[date], Optional[date]]:
        """Get available date range for exchange rates in database"""
        try:
            min_date = (
                self.db.query(ExchangeRateRecord.date)
                .order_by(ExchangeRateRecord.date.asc())
                .first()
            )
            max_date = (
                self.db.query(ExchangeRateRecord.date)
                .order_by(ExchangeRateRecord.date.desc())
                .first()
            )

            return (
                min_date[0] if min_date else None,
                max_date[0] if max_date else None,
            )

        except Exception as e:
            logger.error(f"Error getting exchange rate date range: {e}")
            return None, None

    def get_available_currencies(self) -> List[str]:
        """Get list of available currencies in database"""
        try:
            currencies = self.db.query(ExchangeRateRecord.currency).distinct().all()
            return sorted([currency[0] for currency in currencies])
        except Exception as e:
            logger.error(f"Error getting available currencies: {e}")
            return []


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
