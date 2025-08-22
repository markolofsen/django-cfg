from typing import *

from pydantic import BaseModel, Field


class UserList(BaseModel):
    """
    None model
        Serializer for user list view.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: int = Field(validation_alias="id")

    username: str = Field(validation_alias="username")

    email: str = Field(validation_alias="email")

    first_name: Optional[str] = Field(validation_alias="first_name", default=None)

    last_name: Optional[str] = Field(validation_alias="last_name", default=None)

    full_name: str = Field(validation_alias="full_name")

    is_active: Optional[bool] = Field(validation_alias="is_active", default=None)

    date_joined: str = Field(validation_alias="date_joined")
