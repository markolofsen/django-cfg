from typing import *

from pydantic import BaseModel, Field

from .Author import Author
from .ReactionEnum import ReactionEnum


class PostLike(BaseModel):
    """
    None model
        Serializer for post likes.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: int = Field(validation_alias="id")

    user: Author = Field(validation_alias="user")

    reaction: Optional[ReactionEnum] = Field(validation_alias="reaction", default=None)

    created_at: str = Field(validation_alias="created_at")
