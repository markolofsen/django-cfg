from typing import *

from pydantic import BaseModel, Field


class UserCreateRequest(BaseModel):
    """
    None model
        Serializer for user creation.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    username: str = Field(validation_alias="username")

    email: str = Field(validation_alias="email")

    first_name: Optional[str] = Field(validation_alias="first_name", default=None)

    last_name: Optional[str] = Field(validation_alias="last_name", default=None)

    password: str = Field(validation_alias="password")

    password_confirm: str = Field(validation_alias="password_confirm")
