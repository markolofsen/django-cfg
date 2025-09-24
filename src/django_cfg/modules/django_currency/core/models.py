"""
Simple data models for currency conversion.
"""

from datetime import datetime
from typing import Optional, List, Set
from pydantic import BaseModel, Field


class Rate(BaseModel):
    """Currency exchange rate model."""
    
    source: str = Field(description="Data source (yfinance, coingecko)")
    base_currency: str = Field(description="Base currency code")
    quote_currency: str = Field(description="Quote currency code") 
    rate: float = Field(description="Exchange rate")
    timestamp: datetime = Field(default_factory=datetime.now, description="Rate timestamp")


class ConversionRequest(BaseModel):
    """Currency conversion request model."""
    
    amount: float = Field(gt=0, description="Amount to convert")
    from_currency: str = Field(description="Source currency code")
    to_currency: str = Field(description="Target currency code")


class ConversionResult(BaseModel):
    """Currency conversion result model."""
    
    request: ConversionRequest = Field(description="Original request")
    result: float = Field(description="Converted amount")
    rate: Rate = Field(description="Exchange rate used")
    path: Optional[str] = Field(default=None, description="Conversion path if indirect")


class YFinanceCurrencies(BaseModel):
    """YFinance supported currencies model."""
    
    fiat: List[str] = Field(description="Supported fiat currencies")


class CoinGeckoCurrencies(BaseModel):
    """CoinGecko supported currencies model."""
    
    crypto: List[str] = Field(description="Supported cryptocurrencies")
    vs_currencies: List[str] = Field(description="Supported quote currencies")


class SupportedCurrencies(BaseModel):
    """All supported currencies model."""
    
    yfinance: YFinanceCurrencies = Field(description="YFinance currencies")
    coingecko: CoinGeckoCurrencies = Field(description="CoinGecko currencies")
