from datetime import date
from typing import Any, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from src.utils.constants import MAX_VALID_YEAR, MIN_VALID_YEAR, VALID_CURRENCY_CODES


class UIValueModel(BaseModel):
    date: date
    value: float = Field(gt=0, description="UI value must be positive")


class URValueModel(BaseModel):
    year: int = Field(ge=MIN_VALID_YEAR, le=MAX_VALID_YEAR)
    month: int = Field(ge=1, le=12)
    value: float = Field(gt=0, description="UR value must be positive")

    @field_validator("month")
    def validate_month(cls, v: int) -> int:
        if not 1 <= v <= 12:
            raise ValueError("Month must be between 1 and 12")
        return v


class UIRangeRequestModel(BaseModel):
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.end_date < self.start_date:
            raise ValueError("End date must be after or equal to start date")
        return self


class URRangeRequestModel(BaseModel):
    start_year: int = Field(ge=MIN_VALID_YEAR, le=MAX_VALID_YEAR)
    start_month: int = Field(ge=1, le=12, default=1)
    end_year: Optional[int] = Field(None, ge=MIN_VALID_YEAR, le=MAX_VALID_YEAR)
    end_month: int = Field(ge=1, le=12, default=12)

    @model_validator(mode="after")
    def validate_range(self):
        if self.end_year is None:
            self.end_year = self.start_year

        if (self.end_year < self.start_year) or (
            self.end_year == self.start_year and self.end_month < self.start_month
        ):
            raise ValueError("End period must be after start period")
        return self


class ExchangeRateValueModel(BaseModel):
    date: date
    currency: str = Field(min_length=3, max_length=3)
    buy_rate: float = Field(gt=0)
    sell_rate: float = Field(gt=0)
    average_rate: Optional[float] = Field(None, gt=0)
    arbitrage: Optional[str] = Field(None, max_length=50)

    @field_validator("currency")
    def validate_currency(cls, v: str) -> str:
        if v.upper() not in VALID_CURRENCY_CODES:
            raise ValueError(
                f'Invalid currency code. Must be one of: {", ".join(VALID_CURRENCY_CODES)}'
            )
        return v.upper()


class ExchangeRateRangeRequestModel(BaseModel):
    start_date: date
    end_date: date
    currency: Optional[str] = Field(None, min_length=3, max_length=3)

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.end_date < self.start_date:
            raise ValueError("End date must be after or equal to start date")
        return self

    @field_validator("currency")
    def validate_currency(cls, v: Optional[str]) -> Optional[str]:
        if v and v.upper() not in VALID_CURRENCY_CODES:
            raise ValueError(
                f'Invalid currency code. Must be one of: {", ".join(VALID_CURRENCY_CODES)}'
            )
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


class TOTPVerifyRequest(BaseModel):
    """Request model for TOTP code verification"""

    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")

    @field_validator("code")
    def validate_code_format(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("TOTP code must contain only digits")
        return v


class TOTPVerifyResponse(BaseModel):
    """Response model for successful TOTP verification"""

    access: str = "granted"
    session_token: str
    expires_in: int
    message: str = "Access granted to monitoring dashboard"

