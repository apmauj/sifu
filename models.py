from datetime import date
from typing import Optional, Any


class UIValue:
    def __init__(self, date: date, value: float):
        self.date = date
        self.value = value
    
    def dict(self):
        return {
            "date": self.date.isoformat() if isinstance(self.date, date) else self.date,
            "value": self.value
        }


class URValue:
    def __init__(self, year: int = None, month: int = None, value: float = None, **kwargs):
        """UR value with flexible constructor.

    Accepts English (year, month, value) and legacy Spanish aliases (año/ano, mes, valor).
        """
        if year is None and 'año' in kwargs:
            year = kwargs.pop('año')
        if month is None and 'mes' in kwargs:
            month = kwargs.pop('mes')
        if value is None and 'valor' in kwargs:
            value = kwargs.pop('valor')
        self.year = year
        self.month = month
        self.value = value

    # Legacy Spanish alias properties (año/mes/valor)
    @property
    def año(self):  # type: ignore
        return self.year

    @año.setter
    def año(self, v):  # type: ignore
        self.year = v

    @property
    def mes(self):  # type: ignore
        return self.month

    @mes.setter
    def mes(self, v):  # type: ignore
        self.month = v

    @property
    def valor(self):  # type: ignore
        return self.value

    @valor.setter
    def valor(self, v):  # type: ignore
        self.value = v
    
    def dict(self):
        # Provide both English and legacy Spanish keys to maintain backward compatibility with tests
        return {
            "year": self.year,
            "month": self.month,
            "value": self.value,
            "año": self.year,
            "mes": self.month,
            "valor": self.value,
        }


class ExchangeRateValue:
    def __init__(self, date: date, currency: str, buy_rate: Optional[float] = None, 
                 sell_rate: Optional[float] = None, average_rate: Optional[float] = None,
                 arbitrage: Optional[float] = None):
        self.date = date
        self.currency = currency
        self.buy_rate = buy_rate
        self.sell_rate = sell_rate
        self.average_rate = average_rate
        self.arbitrage = arbitrage
    
    def dict(self):
        return {
            "date": self.date.isoformat() if isinstance(self.date, date) else self.date,
            "currency": self.currency,
            "buy_rate": self.buy_rate,
            "sell_rate": self.sell_rate,
            "average_rate": self.average_rate,
            "arbitrage": self.arbitrage
        }


class UIRangeRequest:
    def __init__(self, start_date: date, end_date: date):
        self.start_date = start_date
        self.end_date = end_date


class URRangeRequest:
    def __init__(self, start_year: int, start_month: int = 1, end_year: int = None, end_month: int = 12):
        self.start_year = start_year
        self.start_month = start_month
        self.end_year = end_year or start_year
        self.end_month = end_month


class UIResponse:
    def __init__(self, success: bool = True, message: str = "", data: Optional[Any] = None):
        self.success = success
        self.message = message
        self.data = data
    
    def dict(self):
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data
        }


class URResponse:
    def __init__(self, success: bool = True, message: str = "", data: Optional[Any] = None):
        self.success = success
        self.message = message
        self.data = data
    
    def dict(self):
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data
        }


class ExchangeRateResponse:
    def __init__(self, success: bool = True, message: str = "", data: Optional[Any] = None):
        self.success = success
        self.message = message
        self.data = data
    
    def dict(self):
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data
        }


class RefreshResponse:
    def __init__(self, success: bool = True, message: str = "", total_records: int = 0, last_updated: Optional[date] = None):
        self.success = success
        self.message = message
        self.total_records = total_records
        self.last_updated = last_updated
    
    def dict(self):
        return {
            "success": self.success,
            "message": self.message,
            "total_records": self.total_records,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }


class BROUValue:
    def __init__(self, currency: str, name: str, buy_rate: Optional[float] = None, 
                 sell_rate: Optional[float] = None, average_rate: Optional[float] = None,
                 arbitrage_buy: Optional[float] = None, arbitrage_sell: Optional[float] = None,
                 source: str = 'BROU', timestamp: Optional[str] = None):
        self.currency = currency
        self.name = name
        self.buy_rate = buy_rate
        self.sell_rate = sell_rate
        self.average_rate = average_rate
        self.arbitrage_buy = arbitrage_buy
        self.arbitrage_sell = arbitrage_sell
        self.source = source
        self.timestamp = timestamp
    
    def dict(self):
        return {
            "currency": self.currency,
            "name": self.name,
            "buy_rate": self.buy_rate,
            "sell_rate": self.sell_rate,
            "average_rate": self.average_rate,
            "arbitrage_buy": self.arbitrage_buy,
            "arbitrage_sell": self.arbitrage_sell,
            "source": self.source,
            "timestamp": self.timestamp
        }


class ExchangeRateRangeRequest:
    def __init__(self, start_date: date, end_date: date, currency: Optional[str] = None):
        self.start_date = start_date
        self.end_date = end_date
        self.currency = currency  # Filter by specific currency


class BROUResponse:
    def __init__(self, success: bool = True, message: str = "", data: Optional[Any] = None, 
                 source: str = 'BROU', timestamp: Optional[str] = None):
        self.success = success
        self.message = message
        self.data = data
        self.source = source
        self.timestamp = timestamp
    
    def dict(self):
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "source": self.source,
            "timestamp": self.timestamp
        } 