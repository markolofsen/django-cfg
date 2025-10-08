from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..enums import ProductDetailstatus


class PaginatedProductListList(BaseModel):
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



class ProductDetail(BaseModel):
    """
    Serializer for product detail view.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: int = ...
    name: str = Field(max_length=200)
    slug: str = Field(None, max_length=200, pattern='^[-a-zA-Z0-9_]+$')
    description: str = ...
    short_description: str = Field(None, max_length=500)
    price: str = Field(pattern='^-?\\d{0,8}(?:\\.\\d{0,2})?$')
    sale_price: str | None = Field(None, pattern='^-?\\d{0,8}(?:\\.\\d{0,2})?$')
    current_price: str = Field(pattern='^-?\\d{0,8}(?:\\.\\d{0,2})?$')
    is_on_sale: bool = ...
    discount_percentage: int = ...
    sku: str = Field(max_length=100)
    stock_quantity: int = Field(None, ge=0.0, le=9.223372036854776e+18)
    manage_stock: bool = None
    is_in_stock: bool = ...
    category: dict[str, Any] = ...
    image: str | None = None
    status: ProductDetailStatus = Field(None, description='* `active` - Active\n* `inactive` - Inactive\n* `out_of_stock` - Out of Stock')
    is_featured: bool = None
    is_digital: bool = None
    meta_title: str = Field(None, max_length=60)
    meta_description: str = Field(None, max_length=160)
    views_count: int = Field(None, ge=0.0, le=9.223372036854776e+18)
    sales_count: int = Field(None, ge=0.0, le=9.223372036854776e+18)
    weight: str | None = Field(None, description='Weight in kg', pattern='^-?\\d{0,6}(?:\\.\\d{0,2})?$')
    length: str | None = Field(None, description='Length in cm', pattern='^-?\\d{0,6}(?:\\.\\d{0,2})?$')
    width: str | None = Field(None, description='Width in cm', pattern='^-?\\d{0,6}(?:\\.\\d{0,2})?$')
    height: str | None = Field(None, description='Height in cm', pattern='^-?\\d{0,6}(?:\\.\\d{0,2})?$')
    created_at: str = ...
    updated_at: str = ...



class ShopStats(BaseModel):
    """
    Serializer for shop statistics.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    total_products: int = ...
    active_products: int = ...
    out_of_stock_products: int = ...
    total_orders: int = ...
    pending_orders: int = ...
    total_revenue: str = Field(pattern='^-?\\d{0,10}(?:\\.\\d{0,2})?$')
    popular_products: list[dict[str, Any]] = ...
    recent_orders: list[dict[str, Any]] = ...



