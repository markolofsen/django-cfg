from typing import *

from pydantic import BaseModel, Field


class Tag(BaseModel):
    """
    None model
        Serializer for blog tags.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: int = Field(validation_alias="id")

    name: str = Field(validation_alias="name")

    slug: str = Field(validation_alias="slug")

    description: Optional[str] = Field(validation_alias="description", default=None)

    posts_count: int = Field(validation_alias="posts_count")

    created_at: str = Field(validation_alias="created_at")
