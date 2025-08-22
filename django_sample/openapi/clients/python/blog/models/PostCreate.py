from typing import *

from pydantic import BaseModel, Field

from .StatusEnum import StatusEnum


class PostCreate(BaseModel):
    """
    None model
        Serializer for post creation.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    title: str = Field(validation_alias="title")

    content: str = Field(validation_alias="content")

    excerpt: Optional[str] = Field(validation_alias="excerpt", default=None)

    category: Optional[int] = Field(validation_alias="category", default=None)

    tags: Optional[List[int]] = Field(validation_alias="tags", default=None)

    status: Optional[StatusEnum] = Field(validation_alias="status", default=None)

    is_featured: Optional[bool] = Field(validation_alias="is_featured", default=None)

    allow_comments: Optional[bool] = Field(validation_alias="allow_comments", default=None)

    meta_title: Optional[str] = Field(validation_alias="meta_title", default=None)

    meta_description: Optional[str] = Field(validation_alias="meta_description", default=None)

    meta_keywords: Optional[str] = Field(validation_alias="meta_keywords", default=None)

    featured_image: Optional[str] = Field(validation_alias="featured_image", default=None)

    featured_image_alt: Optional[str] = Field(validation_alias="featured_image_alt", default=None)
