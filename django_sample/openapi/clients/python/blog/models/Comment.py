from typing import *

from pydantic import BaseModel, Field

from .Author import Author


class Comment(BaseModel):
    """
    None model
        Serializer for blog comments.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: int = Field(validation_alias="id")

    content: str = Field(validation_alias="content")

    author: Author = Field(validation_alias="author")

    parent: Optional[int] = Field(validation_alias="parent", default=None)

    is_approved: bool = Field(validation_alias="is_approved")

    likes_count: int = Field(validation_alias="likes_count")

    replies: str = Field(validation_alias="replies")

    can_edit: str = Field(validation_alias="can_edit")

    created_at: str = Field(validation_alias="created_at")

    updated_at: str = Field(validation_alias="updated_at")
