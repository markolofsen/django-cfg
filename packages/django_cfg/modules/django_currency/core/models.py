"""
Data models for currency conversion and API responses.
"""

from datetime import datetime
from typing import Optional, List, Set, Dict, Any
from pydantic import BaseModel, Field, RootModel


class Rate(BaseModel):
    """Currency exchange rate model."""
    
    source: str = Field(description="Data source (yahoo, coinpaprika)")
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


class YahooFinanceCurrencies(BaseModel):
    """Yahoo Finance supported currencies model."""
    
    fiat: List[str] = Field(description="Supported fiat currencies")


class CoinPaprikaCurrencies(BaseModel):
    """CoinPaprika supported currencies model."""
    
    crypto: List[str] = Field(description="Supported cryptocurrencies")


class SupportedCurrencies(BaseModel):
    """All supported currencies model."""
    
    yahoo: YahooFinanceCurrencies = Field(description="Yahoo Finance currencies")
    coinpaprika: CoinPaprikaCurrencies = Field(description="CoinPaprika currencies")


# ============================================================================
# API RESPONSE MODELS
# ============================================================================

class YahooFinanceTradingPeriod(BaseModel):
    """Yahoo Finance trading period."""
    start: int
    end: int
    timezone: str
    gmtoffset: int


class YahooFinanceCurrentTradingPeriod(BaseModel):
    """Yahoo Finance current trading period."""
    pre: YahooFinanceTradingPeriod
    regular: YahooFinanceTradingPeriod
    post: YahooFinanceTradingPeriod


class YahooFinanceMeta(BaseModel):
    """Yahoo Finance chart meta data."""
    currency: str
    symbol: str
    exchangeName: str
    fullExchangeName: str
    instrumentType: str
    firstTradeDate: int
    regularMarketTime: int
    hasPrePostMarketData: bool
    gmtoffset: int
    timezone: str
    exchangeTimezoneName: str
    regularMarketPrice: float
    fiftyTwoWeekHigh: Optional[float] = None
    fiftyTwoWeekLow: Optional[float] = None
    regularMarketDayHigh: Optional[float] = None
    regularMarketDayLow: Optional[float] = None
    regularMarketVolume: Optional[int] = None
    longName: Optional[str] = None
    shortName: Optional[str] = None
    chartPreviousClose: Optional[float] = None
    previousClose: Optional[float] = None
    scale: Optional[int] = None
    priceHint: Optional[int] = None
    currentTradingPeriod: Optional[YahooFinanceCurrentTradingPeriod] = None
    tradingPeriods: Optional[List[List[YahooFinanceTradingPeriod]]] = None
    dataGranularity: Optional[str] = None
    range: Optional[str] = None
    validRanges: Optional[List[str]] = None


class YahooFinanceResult(BaseModel):
    """Yahoo Finance chart result."""
    meta: YahooFinanceMeta


class YahooFinanceChart(BaseModel):
    """Yahoo Finance chart response."""
    result: List[YahooFinanceResult]
    error: Optional[str] = None


class YahooFinanceResponse(BaseModel):
    """Complete Yahoo Finance API response."""
    chart: YahooFinanceChart


class CoinPaprikaQuoteUSD(BaseModel):
    """CoinPaprika USD quote data."""
    price: float
    volume_24h: Optional[float] = None
    volume_24h_change_24h: Optional[float] = None
    market_cap: Optional[float] = None
    market_cap_change_24h: Optional[float] = None
    percent_change_15m: Optional[float] = None
    percent_change_30m: Optional[float] = None
    percent_change_1h: Optional[float] = None
    percent_change_6h: Optional[float] = None
    percent_change_12h: Optional[float] = None
    percent_change_24h: Optional[float] = None
    percent_change_7d: Optional[float] = None
    percent_change_30d: Optional[float] = None
    percent_change_1y: Optional[float] = None
    ath_price: Optional[float] = None
    ath_date: Optional[str] = None
    percent_from_price_ath: Optional[float] = None


class CoinPaprikaQuotes(BaseModel):
    """CoinPaprika quotes container."""
    USD: CoinPaprikaQuoteUSD


class CoinPaprikaTicker(BaseModel):
    """CoinPaprika ticker data."""
    id: str
    name: str
    symbol: str
    rank: int
    total_supply: Optional[float] = None
    max_supply: Optional[float] = None
    beta_value: Optional[float] = None
    first_data_at: Optional[str] = None
    last_updated: str
    quotes: CoinPaprikaQuotes


class CoinPaprikaTickersResponse(RootModel):
    """CoinPaprika tickers response (list of tickers)."""
    root: List[CoinPaprikaTicker]
