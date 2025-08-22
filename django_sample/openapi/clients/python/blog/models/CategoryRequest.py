from typing import *

from pydantic import BaseModel, Field


class CategoryRequest(BaseModel):
    """
    None model
        Serializer for blog categories.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    name: str = Field(validation_alias="name")

    description: Optional[str] = Field(validation_alias="description", default=None)

    color: Optional[str] = Field(validation_alias="color", default=None)

    meta_title: Optional[str] = Field(validation_alias="meta_title", default=None)

    meta_description: Optional[str] = Field(validation_alias="meta_description", default=None)

    parent: Optional[int] = Field(validation_alias="parent", default=None)
