from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    """Serializer for user details.

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: int = ...
    email: str = ...
    first_name: str = Field(None, max_length=50)
    last_name: str = Field(None, max_length=50)
    full_name: str = Field(description="Get user's full name.")
    initials: str = Field(description="Get user's initials for avatar fallback.")
    display_username: str = Field(description='Get formatted username for display.')
    company: str = Field(None, max_length=100)
    phone: str = Field(None, max_length=20)
    position: str = Field(None, max_length=100)
    avatar: str | None = None
    is_staff: bool = Field(description='Designates whether the user can log into this admin site.')
    is_superuser: bool = Field(description='Designates that this user has all permissions without explicitly assigning them.')
    date_joined: str = ...
    last_login: str | None = ...
    unanswered_messages_count: int = Field(description='Get count of unanswered messages for the user.')



class UserProfileUpdateRequest(BaseModel):
    """Serializer for updating user profile.

Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    first_name: str = Field(None, max_length=50)
    last_name: str = Field(None, max_length=50)
    company: str = Field(None, max_length=100)
    phone: str = Field(None, max_length=20)
    position: str = Field(None, max_length=100)



class PatchedUserProfileUpdateRequest(BaseModel):
    """Serializer for updating user profile.

Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    first_name: str = Field(None, max_length=50)
    last_name: str = Field(None, max_length=50)
    company: str = Field(None, max_length=100)
    phone: str = Field(None, max_length=20)
    position: str = Field(None, max_length=100)



