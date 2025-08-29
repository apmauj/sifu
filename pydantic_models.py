from pydantic import BaseModel, Field, validator
from typing import Optional, List, Any
from datetime import date
from constants import VALID_CURRENCY_CODES, MIN_VALID_YEAR, MAX_VALID_YEAR

class UIValueModel(BaseModel):
    date: date
    value: float = Field(gt=0, description="UI value must be positive")

class URValueModel(BaseModel):
    year: int = Field(ge=MIN_VALID_YEAR, le=MAX_VALID_YEAR)
    month: int = Field(ge=1, le=12)
    value: float = Field(gt=0, description="UR value must be positive")

    @validator('month')
    def validate_month(cls, v):
        if not 1 <= v <= 12:
            raise ValueError('Month must be between 1 and 12')
        return v

class UIRangeRequestModel(BaseModel):
    start_date: date
    end_date: date

    @validator('end_date')
    def validate_date_range(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('End date must be after or equal to start date')
        return v

class URRangeRequestModel(BaseModel):
    start_year: int = Field(ge=MIN_VALID_YEAR, le=MAX_VALID_YEAR)
    start_month: int = Field(ge=1, le=12, default=1)
    end_year: Optional[int] = Field(None, ge=MIN_VALID_YEAR, le=MAX_VALID_YEAR)
    end_month: int = Field(ge=1, le=12, default=12)

    @validator('end_year', always=True)
    def set_end_year(cls, v, values):
        return v or values.get('start_year', 2024)

    @validator('end_month')
    def validate_range(cls, v, values):
        start_year = values.get('start_year')
        start_month = values.get('start_month')
        end_year = values.get('end_year')

        if start_year and end_year and start_month is not None:
            if (end_year < start_year) or (end_year == start_year and v < start_month):
                raise ValueError('End period must be after start period')
        return v

class ExchangeRateValueModel(BaseModel):
    date: date
    currency: str = Field(min_length=3, max_length=3)
    buy_rate: float = Field(gt=0)
    sell_rate: float = Field(gt=0)
    average_rate: Optional[float] = Field(None, gt=0)
    arbitrage: Optional[str] = Field(None, max_length=50)

    @validator('currency')
    def validate_currency(cls, v):
        if v.upper() not in VALID_CURRENCY_CODES:
            raise ValueError(f'Invalid currency code. Must be one of: {", ".join(VALID_CURRENCY_CODES)}')
        return v.upper()

class ExchangeRateRangeRequestModel(BaseModel):
    start_date: date
    end_date: date
    currency: Optional[str] = Field(None, min_length=3, max_length=3)

    @validator('end_date')
    def validate_date_range(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('End date must be after or equal to start date')
        return v

    @validator('currency')
    def validate_currency(cls, v):
        if v and v.upper() not in VALID_CURRENCY_CODES:
            raise ValueError(f'Invalid currency code. Must be one of: {", ".join(VALID_CURRENCY_CODES)}')
        return v.upper() if v else v

class APIResponse(BaseModel):
    success: bool
    message: str = Field(max_length=500)
    data: Optional[Any] = None

class PaginatedResponse(BaseModel):
    success: bool
    message: str = Field(max_length=500)
    data: Optional[List[Any]] = None
    total_count: Optional[int] = Field(None, ge=0)
    page: Optional[int] = Field(None, ge=1)
    page_size: Optional[int] = Field(None, ge=1, le=1000)
