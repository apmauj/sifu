from datetime import date
from types import SimpleNamespace

from src.domain.exchange_rate_mapping_utils import (
    map_exchange_rate_record,
    map_exchange_rate_records,
)


def _make_record(currency: str = "USD", day: int = 1):
    return SimpleNamespace(
        date=date(2026, 1, day),
        currency=currency,
        buy_rate=41.10,
        sell_rate=42.20,
        average_rate=41.65,
        arbitrage=0.15,
    )


def test_map_exchange_rate_record_builds_domain_value():
    record = _make_record("EUR", 2)

    mapped = map_exchange_rate_record(record)

    assert mapped.date == date(2026, 1, 2)
    assert mapped.currency == "EUR"
    assert mapped.buy_rate == 41.10
    assert mapped.sell_rate == 42.20
    assert mapped.average_rate == 41.65
    assert mapped.arbitrage == 0.15


def test_map_exchange_rate_records_maps_all_records():
    records = [_make_record("USD", 1), _make_record("ARS", 3)]

    mapped = map_exchange_rate_records(records)

    assert len(mapped) == 2
    assert mapped[0].currency == "USD"
    assert mapped[1].currency == "ARS"
