from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PaginatedBlogCategoryList(BaseModel):
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



class BlogCategoryRequest(BaseModel):
    """Serializer for blog categories.

Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    name: str = Field(min_length=1, max_length=100)
    description: str = None
    color: str = Field(None, description='Hex color code', min_length=1, max_length=7)
    meta_title: str = Field(None, max_length=60)
    meta_description: str = Field(None, max_length=160)
    parent: int | None = None



class BlogCategory(BaseModel):
    """Serializer for blog categories.

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
    color: str = Field(None, description='Hex color code', max_length=7)
    meta_title: str = Field(None, max_length=60)
    meta_description: str = Field(None, max_length=160)
    parent: int | None = None
    posts_count: int = ...
    children: list[dict[str, Any]] = ...
    created_at: str = ...
    updated_at: str = ...



