from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..enums import OrderDetail.status


class PaginatedOrderListList(BaseModel):
    """
Response model (includes read-only fields)."""

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



class OrderDetail(BaseModel):
    """Serializer for order detail view.

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: int = ...
    order_number: str = Field(max_length=50)
    customer: str = ...
    status: OrderDetail.status = Field(None, description='* `pending` - Pending\n* `processing` - Processing\n* `shipped` - Shipped\n* `delivered` - Delivered\n* `cancelled` - Cancelled\n* `refunded` - Refunded')
    subtotal: str = Field(None, pattern='^-?\\d{0,8}(?:\\.\\d{0,2})?$')
    tax_amount: str = Field(None, pattern='^-?\\d{0,8}(?:\\.\\d{0,2})?$')
    shipping_amount: str = Field(None, pattern='^-?\\d{0,8}(?:\\.\\d{0,2})?$')
    discount_amount: str = Field(None, pattern='^-?\\d{0,8}(?:\\.\\d{0,2})?$')
    total_amount: str = Field(None, pattern='^-?\\d{0,8}(?:\\.\\d{0,2})?$')
    billing_address: str = ...
    shipping_address: str = ...
    customer_notes: str = None
    admin_notes: str = None
    items: list[dict[str, Any]] = ...
    created_at: str = ...
    updated_at: str = ...
    shipped_at: str | None = None
    delivered_at: str | None = None



