from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PaginatedEmailLogList(BaseModel):
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



