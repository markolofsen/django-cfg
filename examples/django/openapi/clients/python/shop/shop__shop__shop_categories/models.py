from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PaginatedShopCategoryList(BaseModel):
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



class ShopCategory(BaseModel):
    """Serializer for shop categories.

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: int = ...
    name: str = Field(max_length=100)
    slug: str = Field(pattern='^[-a-zA-Z0-9_]+$')
    description: str = None
    image: str | None = None
    parent: int | None = None
    meta_title: str = Field(None, max_length=60)
    meta_description: str = Field(None, max_length=160)
    products_count: int = ...
    children: list[dict[str, Any]] = ...
    is_active: bool = None
    sort_order: int = Field(None, ge=0.0, le=9.223372036854776e+18)
    created_at: str = ...
    updated_at: str = ...



