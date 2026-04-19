from datetime import date
from typing import List, Optional
import logging

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.domain.models import ExchangeRateValue
from src.infrastructure.database import ExchangeRateRecord

logger = logging.getLogger(__name__)


class ExchangeRateService:
    def __init__(self, db: Session):
        self.db = db

    def get_exchange_rate_by_date(
        self, date: date, currency: Optional[str] = None
    ) -> List[ExchangeRateValue]:
        """Get exchange rates for a specific date, optionally filtered by currency."""
        try:
            query = self.db.query(ExchangeRateRecord).filter(
                ExchangeRateRecord.date == date
            )

            if currency:
                if "," in currency:
                    currency_list = [c.strip().upper() for c in currency.split(",")]
                    query = query.filter(ExchangeRateRecord.currency.in_(currency_list))
                else:
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
        """Get recent exchange rates for a specific currency."""
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
        """Get exchange rates for a date range, optionally filtered by currency."""
        try:
            query = self.db.query(ExchangeRateRecord).filter(
                and_(
                    ExchangeRateRecord.date >= start_date,
                    ExchangeRateRecord.date <= end_date,
                )
            )

            if currency:
                if "," in currency:
                    currency_list = [c.strip().upper() for c in currency.split(",")]
                    query = query.filter(ExchangeRateRecord.currency.in_(currency_list))
                else:
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
        """Get the most recent exchange rates for all or specified currencies."""
        try:
            latest_date_query = (
                self.db.query(ExchangeRateRecord.date)
                .order_by(ExchangeRateRecord.date.desc())
                .first()
            )

            if not latest_date_query:
                return []

            latest_date = latest_date_query[0]

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
        """Get exchange rate closest to a date for a specific currency."""
        try:
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
            return None

        except Exception as e:
            logger.error(
                f"Error getting exchange rate closest to {target_date} for {currency}: {e}"
            )
            return None

    def get_total_records(self) -> int:
        """Get total number of exchange rate records in database."""
        try:
            return self.db.query(ExchangeRateRecord).count()
        except Exception as e:
            logger.error(f"Error counting exchange rate records: {e}")
            return 0

    def get_date_range_available(self) -> tuple[Optional[date], Optional[date]]:
        """Get available date range for exchange rates in database."""
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
        """Get list of available currencies in database."""
        try:
            currencies = self.db.query(ExchangeRateRecord.currency).distinct().all()
            return sorted([currency[0] for currency in currencies])
        except Exception as e:
            logger.error(f"Error getting available currencies: {e}")
            return []
