from datetime import date
from typing import List, Optional, Dict, Any


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
    def __init__(self, year: int, month: int, value: float):
        self.year = year
        self.month = month
        self.value = value
    
    def dict(self):
        return {
            "year": self.year,
            "month": self.month,
            "value": self.value
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


class ExchangeRateValue:
    def __init__(self, date: date, currency: str, buy_rate: float, sell_rate: float, 
                 average_rate: Optional[float] = None, arbitrage: Optional[str] = None):
        self.date = date
        self.currency = currency  # USD, EUR, ARS, BRL, etc.
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


class ExchangeRateRangeRequest:
    def __init__(self, start_date: date, end_date: date, currency: Optional[str] = None):
        self.start_date = start_date
        self.end_date = end_date
        self.currency = currency  # Filter by specific currency


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