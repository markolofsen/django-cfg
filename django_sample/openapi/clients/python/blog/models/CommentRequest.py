from typing import *

from pydantic import BaseModel, Field


class CommentRequest(BaseModel):
    """
    None model
        Serializer for blog comments.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    content: str = Field(validation_alias="content")

    parent: Optional[int] = Field(validation_alias="parent", default=None)
