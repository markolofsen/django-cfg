from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..enums import PatchedPostUpdateRequest.status, PostUpdate.status


class PatchedBlogCategoryRequest(BaseModel):
    """Serializer for blog categories.

Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    name: str = Field(None, min_length=1, max_length=100)
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



class PatchedPostUpdateRequest(BaseModel):
    """Serializer for post updates.

Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    title: str = Field(None, min_length=1, max_length=200)
    content: str = Field(None, min_length=1)
    excerpt: str = Field(None, description='Brief description', max_length=500)
    category: int | None = None
    tags: list[int] = None
    status: PatchedPostUpdateRequest.status = Field(None, description='* `draft` - Draft\n* `published` - Published\n* `archived` - Archived')
    is_featured: bool = None
    allow_comments: bool = None
    meta_title: str = Field(None, max_length=60)
    meta_description: str = Field(None, max_length=160)
    meta_keywords: str = Field(None, max_length=255)
    featured_image: str | None = None
    featured_image_alt: str = Field(None, max_length=255)



class PostUpdate(BaseModel):
    """Serializer for post updates.

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    title: str = Field(max_length=200)
    content: str = ...
    excerpt: str = Field(None, description='Brief description', max_length=500)
    category: int | None = None
    tags: list[int] = None
    status: PostUpdate.status = Field(None, description='* `draft` - Draft\n* `published` - Published\n* `archived` - Archived')
    is_featured: bool = None
    allow_comments: bool = None
    meta_title: str = Field(None, max_length=60)
    meta_description: str = Field(None, max_length=160)
    meta_keywords: str = Field(None, max_length=255)
    featured_image: str | None = None
    featured_image_alt: str = Field(None, max_length=255)



class Tag(BaseModel):
    """Serializer for blog tags.

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: int = ...
    name: str = Field(max_length=50)
    slug: str = Field(pattern='^[-a-zA-Z0-9_]+$')
    description: str = None
    posts_count: int = ...
    created_at: str = ...



class TagRequest(BaseModel):
    """Serializer for blog tags.

Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    name: str = Field(min_length=1, max_length=50)
    description: str = None



class PatchedTagRequest(BaseModel):
    """Serializer for blog tags.

Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    name: str = Field(None, min_length=1, max_length=50)
    description: str = None



