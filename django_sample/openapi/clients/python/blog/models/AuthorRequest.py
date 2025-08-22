from typing import *

from pydantic import BaseModel, Field


class AuthorRequest(BaseModel):
    """
    None model
        Serializer for post authors.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    username: str = Field(validation_alias="username")

    first_name: Optional[str] = Field(validation_alias="first_name", default=None)

    last_name: Optional[str] = Field(validation_alias="last_name", default=None)

    avatar: Optional[str] = Field(validation_alias="avatar", default=None)
