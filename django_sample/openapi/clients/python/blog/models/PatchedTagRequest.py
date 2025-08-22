from typing import *

from pydantic import BaseModel, Field


class PatchedTagRequest(BaseModel):
    """
    None model
        Serializer for blog tags.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    name: Optional[str] = Field(validation_alias="name", default=None)

    description: Optional[str] = Field(validation_alias="description", default=None)
