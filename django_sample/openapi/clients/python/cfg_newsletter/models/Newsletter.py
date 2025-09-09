from typing import *

from pydantic import BaseModel, Field


class Newsletter(BaseModel):
    """
    None model
        Serializer for Newsletter model.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: int = Field(validation_alias="id")

    title: str = Field(validation_alias="title")

    description: Optional[str] = Field(validation_alias="description", default=None)

    is_active: Optional[bool] = Field(validation_alias="is_active", default=None)

    auto_subscribe: Optional[bool] = Field(validation_alias="auto_subscribe", default=None)

    created_at: str = Field(validation_alias="created_at")

    updated_at: str = Field(validation_alias="updated_at")

    subscribers_count: str = Field(validation_alias="subscribers_count")
