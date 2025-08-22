from typing import *

from pydantic import BaseModel, Field

from .Author import Author
from .Category import Category
from .StatusEnum import StatusEnum
from .Tag import Tag


class PostDetail(BaseModel):
    """
    None model
        Serializer for post detail view.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: int = Field(validation_alias="id")

    title: str = Field(validation_alias="title")

    slug: Optional[str] = Field(validation_alias="slug", default=None)

    content: str = Field(validation_alias="content")

    excerpt: Optional[str] = Field(validation_alias="excerpt", default=None)

    author: Author = Field(validation_alias="author")

    category: Category = Field(validation_alias="category")

    tags: List[Tag] = Field(validation_alias="tags")

    status: Optional[StatusEnum] = Field(validation_alias="status", default=None)

    is_featured: Optional[bool] = Field(validation_alias="is_featured", default=None)

    allow_comments: Optional[bool] = Field(validation_alias="allow_comments", default=None)

    meta_title: Optional[str] = Field(validation_alias="meta_title", default=None)

    meta_description: Optional[str] = Field(validation_alias="meta_description", default=None)

    meta_keywords: Optional[str] = Field(validation_alias="meta_keywords", default=None)

    featured_image: Optional[str] = Field(validation_alias="featured_image", default=None)

    featured_image_alt: Optional[str] = Field(validation_alias="featured_image_alt", default=None)

    views_count: Optional[int] = Field(validation_alias="views_count", default=None)

    likes_count: Optional[int] = Field(validation_alias="likes_count", default=None)

    comments_count: Optional[int] = Field(validation_alias="comments_count", default=None)

    shares_count: Optional[int] = Field(validation_alias="shares_count", default=None)

    published_at: Optional[str] = Field(validation_alias="published_at", default=None)

    created_at: str = Field(validation_alias="created_at")

    updated_at: str = Field(validation_alias="updated_at")

    comments: str = Field(validation_alias="comments")

    user_reaction: str = Field(validation_alias="user_reaction")

    can_edit: str = Field(validation_alias="can_edit")
