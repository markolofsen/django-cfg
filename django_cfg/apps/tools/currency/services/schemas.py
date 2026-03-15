"""Data models for currency conversion."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Rate(BaseModel):
    """Currency exchange rate."""

    source: str = Field(description="Data source (hybrid, coinpaprika)")
    base_currency: str = Field(description="Base currency code")
    quote_currency: str = Field(description="Quote currency code")
    rate: float = Field(description="Exchange rate")
    timestamp: datetime = Field(default_factory=datetime.now)


class ConversionRequest(BaseModel):
    """Currency conversion request."""

    amount: float = Field(gt=0, description="Amount to convert")
    from_currency: str = Field(description="Source currency code")
    to_currency: str = Field(description="Target currency code")


class ConversionResult(BaseModel):
    """Currency conversion result."""

    request: ConversionRequest
    result: float = Field(description="Converted amount")
    rate: Rate = Field(description="Exchange rate used")
    path: Optional[str] = Field(default=None, description="Conversion path if indirect")
