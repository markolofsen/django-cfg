from typing import *

from pydantic import BaseModel, Field


class UserUpdate(BaseModel):
    """
    None model
        Serializer for user updates.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    first_name: Optional[str] = Field(validation_alias="first_name", default=None)

    last_name: Optional[str] = Field(validation_alias="last_name", default=None)

    bio: Optional[str] = Field(validation_alias="bio", default=None)

    location: Optional[str] = Field(validation_alias="location", default=None)

    birth_date: Optional[str] = Field(validation_alias="birth_date", default=None)

    avatar: Optional[str] = Field(validation_alias="avatar", default=None)

    is_public: Optional[bool] = Field(validation_alias="is_public", default=None)

    email_notifications: Optional[bool] = Field(validation_alias="email_notifications", default=None)
