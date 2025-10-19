from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..enums import OrderCreateRequestorder_type, OrderCreateRequestside, OrderCreateorder_type, OrderCreateside, OrderRequestorder_type, OrderRequestside, Orderorder_type, Orderside, Orderstatus, PatchedOrderRequestorder_type, PatchedOrderRequestside


class PaginatedOrderList(BaseModel):
    """
    
    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
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
    results: list[dict[str, Any]] = Field(description='Array of items for current page')



class OrderCreate(BaseModel):
    """
    Serializer for creating orders.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    symbol: str = Field(description='Trading pair (e.g., BTC/USDT)', max_length=20)
    order_type: OrderCreateOrderType = Field(None, description='* `market` - Market\n* `limit` - Limit\n* `stop_loss` - Stop Loss')
    side: OrderCreateSide = Field(description='* `buy` - Buy\n* `sell` - Sell')
    quantity: str = Field(pattern='^-?\\d{0,12}(?:\\.\\d{0,8})?$')
    price: str | None = Field(None, pattern='^-?\\d{0,12}(?:\\.\\d{0,8})?$')



class Order(BaseModel):
    """
    Serializer for orders.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: int = ...
    portfolio: int = ...
    symbol: str = Field(description='Trading pair (e.g., BTC/USDT)', max_length=20)
    order_type: OrderOrderType = Field(None, description='* `market` - Market\n* `limit` - Limit\n* `stop_loss` - Stop Loss')
    side: OrderSide = Field(description='* `buy` - Buy\n* `sell` - Sell')
    quantity: str = Field(pattern='^-?\\d{0,12}(?:\\.\\d{0,8})?$')
    price: str | None = Field(None, pattern='^-?\\d{0,12}(?:\\.\\d{0,8})?$')
    filled_quantity: str = Field(pattern='^-?\\d{0,12}(?:\\.\\d{0,8})?$')
    status: OrderStatus = Field(description='* `pending` - Pending\n* `filled` - Filled\n* `cancelled` - Cancelled')
    total_usd: str = Field(pattern='^-?\\d{0,18}(?:\\.\\d{0,2})?$')
    created_at: str = ...
    updated_at: str = ...



class PaginatedPortfolioList(BaseModel):
    """
    
    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
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
    results: list[dict[str, Any]] = Field(description='Array of items for current page')



class Portfolio(BaseModel):
    """
    Serializer for trading portfolios.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: int = ...
    user: int = ...
    user_info: dict[str, Any] = ...
    total_balance_usd: str = Field(description='Total portfolio value in USD', pattern='^-?\\d{0,18}(?:\\.\\d{0,2})?$')
    available_balance_usd: str = Field(None, description='Available balance for trading', pattern='^-?\\d{0,18}(?:\\.\\d{0,2})?$')
    total_profit_loss: str = Field(pattern='^-?\\d{0,18}(?:\\.\\d{0,2})?$')
    total_trades: int = ...
    winning_trades: int = ...
    losing_trades: int = ...
    win_rate: float = ...
    created_at: str = ...
    updated_at: str = ...



class PortfolioStats(BaseModel):
    """
    Serializer for portfolio statistics.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    total_portfolios: int = ...
    total_volume_usd: str = Field(pattern='^-?\\d{0,18}(?:\\.\\d{0,2})?$')
    total_orders: int = ...



class OrderCreateRequest(BaseModel):
    """
    Serializer for creating orders.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    symbol: str = Field(description='Trading pair (e.g., BTC/USDT)', min_length=1, max_length=20)
    order_type: OrderCreateRequestOrderType = Field(None, description='* `market` - Market\n* `limit` - Limit\n* `stop_loss` - Stop Loss')
    side: OrderCreateRequestSide = Field(description='* `buy` - Buy\n* `sell` - Sell')
    quantity: str = Field(pattern='^-?\\d{0,12}(?:\\.\\d{0,8})?$')
    price: str | None = Field(None, pattern='^-?\\d{0,12}(?:\\.\\d{0,8})?$')



class OrderRequest(BaseModel):
    """
    Serializer for orders.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    portfolio: int = ...
    symbol: str = Field(description='Trading pair (e.g., BTC/USDT)', min_length=1, max_length=20)
    order_type: OrderRequestOrderType = Field(None, description='* `market` - Market\n* `limit` - Limit\n* `stop_loss` - Stop Loss')
    side: OrderRequestSide = Field(description='* `buy` - Buy\n* `sell` - Sell')
    quantity: str = Field(pattern='^-?\\d{0,12}(?:\\.\\d{0,8})?$')
    price: str | None = Field(None, pattern='^-?\\d{0,12}(?:\\.\\d{0,8})?$')



class PatchedOrderRequest(BaseModel):
    """
    Serializer for orders.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    portfolio: int = None
    symbol: str = Field(None, description='Trading pair (e.g., BTC/USDT)', min_length=1, max_length=20)
    order_type: PatchedOrderRequestOrderType = Field(None, description='* `market` - Market\n* `limit` - Limit\n* `stop_loss` - Stop Loss')
    side: PatchedOrderRequestSide = Field(None, description='* `buy` - Buy\n* `sell` - Sell')
    quantity: str = Field(None, pattern='^-?\\d{0,12}(?:\\.\\d{0,8})?$')
    price: str | None = Field(None, pattern='^-?\\d{0,12}(?:\\.\\d{0,8})?$')



