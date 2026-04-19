from collections.abc import Iterable

from src.domain.models import ExchangeRateValue


def map_exchange_rate_record(record) -> ExchangeRateValue:
    """Convert a DB exchange-rate record into the domain value object."""
    return ExchangeRateValue(
        date=record.date,
        currency=record.currency,
        buy_rate=record.buy_rate,
        sell_rate=record.sell_rate,
        average_rate=record.average_rate,
        arbitrage=record.arbitrage,
    )


def map_exchange_rate_records(records: Iterable) -> list[ExchangeRateValue]:
    """Convert an iterable of DB exchange-rate records into domain value objects."""
    return [map_exchange_rate_record(record) for record in records]