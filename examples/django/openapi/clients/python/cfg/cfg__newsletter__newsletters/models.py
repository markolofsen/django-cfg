from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PaginatedNewsletterList(BaseModel):
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



class Newsletter(BaseModel):
    """Serializer for Newsletter model.

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: int = ...
    title: str = Field(max_length=255)
    description: str = None
    is_active: bool = None
    auto_subscribe: bool = Field(None, description='Automatically subscribe new users to this newsletter')
    created_at: str = ...
    updated_at: str = ...
    subscribers_count: int = ...



