from typing import *

from pydantic import BaseModel, Field


class PatchedCommentRequest(BaseModel):
    """
    None model
        Serializer for blog comments.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    content: Optional[str] = Field(validation_alias="content", default=None)

    parent: Optional[int] = Field(validation_alias="parent", default=None)
