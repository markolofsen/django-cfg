from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    """
    Serializer for user details.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    id: int = ...
    email: Any = ...
    first_name: str = Field(None, max_length=50)
    last_name: str = Field(None, max_length=50)
    full_name: Any = Field(description="Get user's full name.")
    initials: Any = Field(description="Get user's initials for avatar fallback.")
    display_username: Any = Field(description='Get formatted username for display.')
    company: str = Field(None, max_length=100)
    phone: str = Field(None, max_length=20)
    position: str = Field(None, max_length=100)
    avatar: Any | None = ...
    is_staff: bool = Field(description='Designates whether the user can log into this admin site.')
    is_superuser: bool = Field(description='Designates that this user has all permissions without explicitly assigning them.')
    date_joined: Any = ...
    last_login: Any | None = ...
    unanswered_messages_count: int = Field(description='Get count of unanswered messages for the user.')



class UserProfileUpdateRequest(BaseModel):
    """
    Serializer for updating user profile.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    first_name: str = Field(None, max_length=50)
    last_name: str = Field(None, max_length=50)
    company: str = Field(None, max_length=100)
    phone: str = Field(None, max_length=20)
    position: str = Field(None, max_length=100)



class PatchedUserProfileUpdateRequest(BaseModel):
    """
    Serializer for updating user profile.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    first_name: str = Field(None, max_length=50)
    last_name: str = Field(None, max_length=50)
    company: str = Field(None, max_length=100)
    phone: str = Field(None, max_length=20)
    position: str = Field(None, max_length=100)



