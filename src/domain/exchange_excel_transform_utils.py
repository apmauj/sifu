import math
from datetime import datetime
from typing import Optional


EXCHANGE_RATE_CURRENCY_MAPPINGS = [
    ("USD", "Dólar.USA.Compra", "Dólar.USA.Venta"),
    ("EUR", "Euro.Compra", "Euro.Venta"),
    ("ARS", "Peso.Argentino.Compra", "Peso.Argentino.Venta"),
    ("BRL", "Real.Compra", "Real.Venta"),
]

EXCHANGE_RATE_DATE_FORMATS = ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d")


def parse_exchange_date_value(date_raw) -> Optional[datetime.date]:
    """Parse a raw exchange date value from INE spreadsheets."""
    if isinstance(date_raw, datetime):
        return date_raw.date()

    if not isinstance(date_raw, str):
        return None

    cleaned = date_raw.split(" ")[0].strip()
    if not cleaned:
        return None

    for fmt in EXCHANGE_RATE_DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue

    return None


def parse_exchange_rate_value(value) -> Optional[float]:
    """Parse a raw exchange-rate value handling decimal separators and invalid values."""
    if value is None or value == ".." or value == "":
        return None

    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return None
        rate = float(value)
    else:
        cleaned = str(value).strip()

        if cleaned == "" or cleaned == "..":
            return None

        if "," in cleaned and "." in cleaned:
            cleaned = cleaned.replace(",", "")
        elif "," in cleaned and "." not in cleaned:
            cleaned = cleaned.replace(",", ".")

        try:
            rate = float(cleaned)
        except (ValueError, TypeError):
            return None

    if rate <= 0 or rate > 10000:
        return None

    return round(rate, 4)