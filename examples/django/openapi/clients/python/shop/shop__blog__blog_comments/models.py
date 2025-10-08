from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PaginatedCommentList(BaseModel):
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



class CommentRequest(BaseModel):
    """Serializer for blog comments.

Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    content: str = Field(min_length=1)
    parent: int | None = None



class Comment(BaseModel):
    """Serializer for blog comments.

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: int = ...
    content: str = ...
    author: dict[str, Any] = ...
    parent: int | None = None
    is_approved: bool = ...
    likes_count: int = ...
    replies: list[dict[str, Any]] = ...
    can_edit: bool = ...
    created_at: str = ...
    updated_at: str = ...



class PatchedCommentRequest(BaseModel):
    """Serializer for blog comments.

Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    content: str = Field(None, min_length=1)
    parent: int | None = None



