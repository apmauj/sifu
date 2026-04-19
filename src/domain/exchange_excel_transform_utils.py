import math
from typing import Optional


EXCHANGE_RATE_CURRENCY_MAPPINGS = [
    ("USD", "Dólar.USA.Compra", "Dólar.USA.Venta"),
    ("EUR", "Euro.Compra", "Euro.Venta"),
    ("ARS", "Peso.Argentino.Compra", "Peso.Argentino.Venta"),
    ("BRL", "Real.Compra", "Real.Venta"),
]


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