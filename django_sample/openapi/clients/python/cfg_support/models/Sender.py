from typing import *

from pydantic import BaseModel, Field


class Sender(BaseModel):
    """
    None model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: int = Field(validation_alias="id")

    display_username: str = Field(validation_alias="display_username")

    email: str = Field(validation_alias="email")

    avatar: str = Field(validation_alias="avatar")

    initials: str = Field(validation_alias="initials")

    is_staff: bool = Field(validation_alias="is_staff")

    is_superuser: bool = Field(validation_alias="is_superuser")
