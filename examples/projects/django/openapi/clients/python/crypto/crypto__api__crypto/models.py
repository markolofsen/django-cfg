from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PaginatedCoinListList(BaseModel):
    """
    
    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    count: int = Field(description='Total number of items across all pages')
    page: int = Field(description='Current page number (1-based)')
    pages: int = Field(description='Total number of pages')
    page_size: int = Field(description='Number of items per page')
    has_next: bool = Field(description='Whether there is a next page')
    has_previous: bool = Field(description='Whether there is a previous page')
    next_page: int | None = Field(None, description='Next page number (null if no next page)')
    previous_page: int | None = Field(None, description='Previous page number (null if no previous page)')
    results: list[Any] = Field(description='Array of items for current page')



class Coin(BaseModel):
    """
    Serializer for coins.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    id: int = ...
    symbol: str = Field(description='Coin symbol (e.g., BTC, ETH)', max_length=10)
    name: str = Field(description='Full name (e.g., Bitcoin, Ethereum)', max_length=100)
    slug: str = Field(max_length=100, pattern='^[-a-zA-Z0-9_]+$')
    current_price_usd: str = Field(None, description='Current price in USD', pattern='^-?\\d{0,12}(?:\\.\\d{0,8})?$')
    market_cap_usd: str = Field(None, description='Market capitalization', pattern='^-?\\d{0,18}(?:\\.\\d{0,2})?$')
    volume_24h_usd: str = Field(None, description='24h trading volume', pattern='^-?\\d{0,18}(?:\\.\\d{0,2})?$')
    price_change_24h_percent: str = Field(None, pattern='^-?\\d{0,8}(?:\\.\\d{0,2})?$')
    price_change_7d_percent: str = Field(None, pattern='^-?\\d{0,8}(?:\\.\\d{0,2})?$')
    price_change_30d_percent: str = Field(None, pattern='^-?\\d{0,8}(?:\\.\\d{0,2})?$')
    logo_url: str = Field(None, max_length=200)
    description: str = None
    website: str = Field(None, max_length=200)
    whitepaper_url: str = Field(None, max_length=200)
    rank: int = Field(None, description='Market cap rank', ge=0, le=2147483647)
    is_active: bool = None
    is_tradeable: bool = None
    is_price_up_24h: bool = ...
    created_at: Any = ...
    updated_at: Any = ...



class CoinStats(BaseModel):
    """
    Serializer for coin statistics.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    total_coins: int = ...
    total_market_cap_usd: str = Field(pattern='^-?\\d{0,18}(?:\\.\\d{0,2})?$')
    total_volume_24h_usd: str = Field(pattern='^-?\\d{0,18}(?:\\.\\d{0,2})?$')
    trending_coins: list[Any] = ...



class PaginatedExchangeList(BaseModel):
    """
    
    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    count: int = Field(description='Total number of items across all pages')
    page: int = Field(description='Current page number (1-based)')
    pages: int = Field(description='Total number of pages')
    page_size: int = Field(description='Number of items per page')
    has_next: bool = Field(description='Whether there is a next page')
    has_previous: bool = Field(description='Whether there is a previous page')
    next_page: int | None = Field(None, description='Next page number (null if no next page)')
    previous_page: int | None = Field(None, description='Previous page number (null if no previous page)')
    results: list[Any] = Field(description='Array of items for current page')



class Exchange(BaseModel):
    """
    Serializer for exchanges.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    id: int = ...
    name: str = Field(description='Exchange name', max_length=100)
    slug: str = Field(max_length=100, pattern='^[-a-zA-Z0-9_]+$')
    code: str = Field(description='Exchange code (e.g., BINANCE, COINBASE)', max_length=20)
    description: str = None
    website: str = Field(None, max_length=200)
    logo_url: str = Field(None, max_length=200)
    volume_24h_usd: str = Field(None, description='24h trading volume', pattern='^-?\\d{0,18}(?:\\.\\d{0,2})?$')
    num_markets: int = Field(None, description='Number of trading pairs', ge=0, le=2147483647)
    num_coins: int = Field(None, description='Number of supported coins', ge=0, le=2147483647)
    maker_fee_percent: str = Field(None, pattern='^-?\\d{0,1}(?:\\.\\d{0,4})?$')
    taker_fee_percent: str = Field(None, pattern='^-?\\d{0,1}(?:\\.\\d{0,4})?$')
    is_active: bool = None
    is_verified: bool = None
    supports_api: bool = None
    rank: int = Field(None, description='Exchange rank by volume', ge=0, le=2147483647)
    created_at: Any = ...
    updated_at: Any = ...



class PaginatedWalletList(BaseModel):
    """
    
    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    count: int = Field(description='Total number of items across all pages')
    page: int = Field(description='Current page number (1-based)')
    pages: int = Field(description='Total number of pages')
    page_size: int = Field(description='Number of items per page')
    has_next: bool = Field(description='Whether there is a next page')
    has_previous: bool = Field(description='Whether there is a previous page')
    next_page: int | None = Field(None, description='Next page number (null if no next page)')
    previous_page: int | None = Field(None, description='Previous page number (null if no previous page)')
    results: list[Any] = Field(description='Array of items for current page')



class Wallet(BaseModel):
    """
    Serializer for wallets.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    id: int = ...
    user: int = ...
    coin: int = ...
    coin_info: Any = ...
    balance: str = Field(None, description='Available balance', pattern='^-?\\d{0,12}(?:\\.\\d{0,8})?$')
    locked_balance: Any = Field(description='Locked balance (in orders)', pattern='^-?\\d{0,12}(?:\\.\\d{0,8})?$')
    total_balance: Any = Field(pattern='^-?\\d{0,12}(?:\\.\\d{0,8})?$')
    value_usd: Any = Field(pattern='^-?\\d{0,12}(?:\\.\\d{0,8})?$')
    address: str = Field(None, description='Deposit address', max_length=200)
    created_at: Any = ...
    updated_at: Any = ...



