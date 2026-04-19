from datetime import date, datetime
from typing import Iterable, Optional


def parse_date_value(value: object, formats: Iterable[str]) -> Optional[date]:
    """Parse a date-like value from string/datetime/date using given formats."""
    if isinstance(value, date) and not isinstance(value, datetime):
        return value

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        for fmt in formats:
            try:
                return datetime.strptime(raw, fmt).date()
            except ValueError:
                continue

    return None


def parse_decimal_value(value: object) -> Optional[float]:
    """Parse decimal values handling formats like 1.234,56 and 1234,56."""
    try:
        if isinstance(value, str):
            raw = value.strip()
            if raw == "":
                return None

            if "," in raw:
                if "." in raw:
                    raw = raw.replace(".", "").replace(",", ".")
                else:
                    raw = raw.replace(",", ".")

            return float(raw)

        return float(value)
    except (ValueError, TypeError):
        return None
