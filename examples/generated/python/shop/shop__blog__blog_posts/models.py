from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..enums import PostCreateRequeststatus, PostCreatestatus, PostDetailRequeststatus, PostDetailstatus, PostUpdateRequeststatus, PostUpdatestatus


class PaginatedPostListList(BaseModel):
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



class PostCreate(BaseModel):
    """
    Serializer for post creation.

    Response model (includes read-only fields).
    """

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
    status: PostCreateStatus = Field(None, description='* `draft` - Draft\n* `published` - Published\n* `archived` - Archived')
    is_featured: bool = None
    allow_comments: bool = None
    meta_title: str = Field(None, max_length=60)
    meta_description: str = Field(None, max_length=160)
    meta_keywords: str = Field(None, max_length=255)
    featured_image: str | None = None
    featured_image_alt: str = Field(None, max_length=255)



class PostDetail(BaseModel):
    """
    Serializer for post detail view.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: int = ...
    title: str = Field(max_length=200)
    slug: str = Field(None, max_length=200, pattern='^[-a-zA-Z0-9_]+$')
    content: str = ...
    excerpt: str = Field(None, description='Brief description', max_length=500)
    author: dict[str, Any] = ...
    category: dict[str, Any] = ...
    tags: list[dict[str, Any]] = ...
    status: PostDetailStatus = Field(None, description='* `draft` - Draft\n* `published` - Published\n* `archived` - Archived')
    is_featured: bool = None
    allow_comments: bool = None
    meta_title: str = Field(None, max_length=60)
    meta_description: str = Field(None, max_length=160)
    meta_keywords: str = Field(None, max_length=255)
    featured_image: str | None = None
    featured_image_alt: str = Field(None, max_length=255)
    views_count: int = Field(None, ge=0.0, le=9.223372036854776e+18)
    likes_count: int = Field(None, ge=0.0, le=9.223372036854776e+18)
    comments_count: int = Field(None, ge=0.0, le=9.223372036854776e+18)
    shares_count: int = Field(None, ge=0.0, le=9.223372036854776e+18)
    published_at: str | None = None
    created_at: str = ...
    updated_at: str = ...
    comments: list[str] = ...
    user_reaction: str | None = ...
    can_edit: bool = ...



class PostUpdate(BaseModel):
    """
    Serializer for post updates.

    Response model (includes read-only fields).
    """

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
    status: PostUpdateStatus = Field(None, description='* `draft` - Draft\n* `published` - Published\n* `archived` - Archived')
    is_featured: bool = None
    allow_comments: bool = None
    meta_title: str = Field(None, max_length=60)
    meta_description: str = Field(None, max_length=160)
    meta_keywords: str = Field(None, max_length=255)
    featured_image: str | None = None
    featured_image_alt: str = Field(None, max_length=255)



class PaginatedPostLikeList(BaseModel):
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



class BlogStats(BaseModel):
    """
    Serializer for blog statistics.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    total_posts: int = ...
    published_posts: int = ...
    draft_posts: int = ...
    total_comments: int = ...
    total_views: int = ...
    total_likes: int = ...
    popular_posts: list[dict[str, Any]] = ...
    recent_posts: list[dict[str, Any]] = ...
    top_categories: list[dict[str, Any]] = ...
    top_tags: list[dict[str, Any]] = ...



class PostCreateRequest(BaseModel):
    """
    Serializer for post creation.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    excerpt: str = Field(None, description='Brief description', max_length=500)
    category: int | None = None
    tags: list[int] = None
    status: PostCreateRequestStatus = Field(None, description='* `draft` - Draft\n* `published` - Published\n* `archived` - Archived')
    is_featured: bool = None
    allow_comments: bool = None
    meta_title: str = Field(None, max_length=60)
    meta_description: str = Field(None, max_length=160)
    meta_keywords: str = Field(None, max_length=255)
    featured_image: str | None = None
    featured_image_alt: str = Field(None, max_length=255)



class PostUpdateRequest(BaseModel):
    """
    Serializer for post updates.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    excerpt: str = Field(None, description='Brief description', max_length=500)
    category: int | None = None
    tags: list[int] = None
    status: PostUpdateRequestStatus = Field(None, description='* `draft` - Draft\n* `published` - Published\n* `archived` - Archived')
    is_featured: bool = None
    allow_comments: bool = None
    meta_title: str = Field(None, max_length=60)
    meta_description: str = Field(None, max_length=160)
    meta_keywords: str = Field(None, max_length=255)
    featured_image: str | None = None
    featured_image_alt: str = Field(None, max_length=255)



class PostDetailRequest(BaseModel):
    """
    Serializer for post detail view.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    title: str = Field(min_length=1, max_length=200)
    slug: str = Field(None, max_length=200, pattern='^[-a-zA-Z0-9_]+$')
    content: str = Field(min_length=1)
    excerpt: str = Field(None, description='Brief description', max_length=500)
    status: PostDetailRequestStatus = Field(None, description='* `draft` - Draft\n* `published` - Published\n* `archived` - Archived')
    is_featured: bool = None
    allow_comments: bool = None
    meta_title: str = Field(None, max_length=60)
    meta_description: str = Field(None, max_length=160)
    meta_keywords: str = Field(None, max_length=255)
    featured_image: str | None = None
    featured_image_alt: str = Field(None, max_length=255)
    views_count: int = Field(None, ge=0.0, le=9.223372036854776e+18)
    likes_count: int = Field(None, ge=0.0, le=9.223372036854776e+18)
    comments_count: int = Field(None, ge=0.0, le=9.223372036854776e+18)
    shares_count: int = Field(None, ge=0.0, le=9.223372036854776e+18)
    published_at: str | None = None



