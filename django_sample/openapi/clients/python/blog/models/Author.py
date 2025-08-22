from typing import *

from pydantic import BaseModel, Field


class Author(BaseModel):
    """
    None model
        Serializer for post authors.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: int = Field(validation_alias="id")

    username: str = Field(validation_alias="username")

    first_name: Optional[str] = Field(validation_alias="first_name", default=None)

    last_name: Optional[str] = Field(validation_alias="last_name", default=None)

    full_name: str = Field(validation_alias="full_name")

    avatar: Optional[str] = Field(validation_alias="avatar", default=None)
