from typing import *

from pydantic import BaseModel, Field

from .UserActivity import UserActivity
from .UserProfile import UserProfile


class UserDetail(BaseModel):
    """
    None model
        Serializer for user detail view.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: int = Field(validation_alias="id")

    username: str = Field(validation_alias="username")

    email: str = Field(validation_alias="email")

    first_name: Optional[str] = Field(validation_alias="first_name", default=None)

    last_name: Optional[str] = Field(validation_alias="last_name", default=None)

    full_name: str = Field(validation_alias="full_name")

    bio: Optional[str] = Field(validation_alias="bio", default=None)

    location: Optional[str] = Field(validation_alias="location", default=None)

    birth_date: Optional[str] = Field(validation_alias="birth_date", default=None)

    avatar: Optional[str] = Field(validation_alias="avatar", default=None)

    is_public: Optional[bool] = Field(validation_alias="is_public", default=None)

    email_notifications: Optional[bool] = Field(validation_alias="email_notifications", default=None)

    is_active: Optional[bool] = Field(validation_alias="is_active", default=None)

    date_joined: str = Field(validation_alias="date_joined")

    created_at: str = Field(validation_alias="created_at")

    updated_at: str = Field(validation_alias="updated_at")

    profile: UserProfile = Field(validation_alias="profile")

    activities: List[UserActivity] = Field(validation_alias="activities")
