from typing import *

from pydantic import BaseModel, Field

from .Category import Category
from .PostList import PostList
from .Tag import Tag


class BlogStats(BaseModel):
    """
    None model
        Serializer for blog statistics.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    total_posts: int = Field(validation_alias="total_posts")

    published_posts: int = Field(validation_alias="published_posts")

    draft_posts: int = Field(validation_alias="draft_posts")

    total_comments: int = Field(validation_alias="total_comments")

    total_views: int = Field(validation_alias="total_views")

    total_likes: int = Field(validation_alias="total_likes")

    popular_posts: List[PostList] = Field(validation_alias="popular_posts")

    recent_posts: List[PostList] = Field(validation_alias="recent_posts")

    top_categories: List[Category] = Field(validation_alias="top_categories")

    top_tags: List[Tag] = Field(validation_alias="top_tags")
