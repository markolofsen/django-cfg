from typing import *

from pydantic import BaseModel, Field


class User(BaseModel):
    """
    None model
        Serializer for user details.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: int = Field(validation_alias="id")

    email: str = Field(validation_alias="email")

    first_name: Optional[str] = Field(validation_alias="first_name", default=None)

    last_name: Optional[str] = Field(validation_alias="last_name", default=None)

    full_name: str = Field(validation_alias="full_name")

    initials: str = Field(validation_alias="initials")

    display_username: str = Field(validation_alias="display_username")

    company: Optional[str] = Field(validation_alias="company", default=None)

    phone: Optional[str] = Field(validation_alias="phone", default=None)

    position: Optional[str] = Field(validation_alias="position", default=None)

    avatar: Optional[str] = Field(validation_alias="avatar", default=None)

    is_staff: bool = Field(validation_alias="is_staff")

    is_superuser: bool = Field(validation_alias="is_superuser")

    date_joined: str = Field(validation_alias="date_joined")

    last_login: str = Field(validation_alias="last_login")

    unanswered_messages_count: int = Field(validation_alias="unanswered_messages_count")
