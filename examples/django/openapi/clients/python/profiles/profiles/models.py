from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PaginatedUserProfileList(BaseModel):
    """
Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    count: int = Field(description='Total number of items across all pages')
    page: int = Field(description='Current page number (1-based)')
    pages: int = Field(description='Total number of pages')
    page_size: int = Field(description='Number of items per page')
    has_next: bool = Field(description='Whether there is a next page')
    has_previous: bool = Field(description='Whether there is a previous page')
    next_page: int | None = Field(None, description='Next page number (null if no next page)')
    previous_page: int | None = Field(None, description='Previous page number (null if no previous page)')
    results: list[dict[str, Any]] = Field(description='Array of items for current page')



class UserProfileRequest(BaseModel):
    """Serializer for user profiles.

Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    website: str = Field(None, max_length=200)
    github: str = Field(None, max_length=100)
    twitter: str = Field(None, max_length=100)
    linkedin: str = Field(None, max_length=100)
    company: str = Field(None, max_length=100)
    job_title: str = Field(None, max_length=100)



class UserProfile(BaseModel):
    """Serializer for user profiles.

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: int = ...
    user: int = ...
    user_info: dict[str, Any] = Field(description='Get basic user information.')
    website: str = Field(None, max_length=200)
    github: str = Field(None, max_length=100)
    twitter: str = Field(None, max_length=100)
    linkedin: str = Field(None, max_length=100)
    company: str = Field(None, max_length=100)
    job_title: str = Field(None, max_length=100)
    posts_count: int = ...
    comments_count: int = ...
    orders_count: int = ...
    created_at: str = ...
    updated_at: str = ...



class UserProfileUpdateRequest(BaseModel):
    """Serializer for updating user profiles.

Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    website: str = Field(None, max_length=200)
    github: str = Field(None, max_length=100)
    twitter: str = Field(None, max_length=100)
    linkedin: str = Field(None, max_length=100)
    company: str = Field(None, max_length=100)
    job_title: str = Field(None, max_length=100)



class UserProfileUpdate(BaseModel):
    """Serializer for updating user profiles.

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    website: str = Field(None, max_length=200)
    github: str = Field(None, max_length=100)
    twitter: str = Field(None, max_length=100)
    linkedin: str = Field(None, max_length=100)
    company: str = Field(None, max_length=100)
    job_title: str = Field(None, max_length=100)



class PatchedUserProfileUpdateRequest(BaseModel):
    """Serializer for updating user profiles.

Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    website: str = Field(None, max_length=200)
    github: str = Field(None, max_length=100)
    twitter: str = Field(None, max_length=100)
    linkedin: str = Field(None, max_length=100)
    company: str = Field(None, max_length=100)
    job_title: str = Field(None, max_length=100)



class PatchedUserProfileRequest(BaseModel):
    """Serializer for user profiles.

Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    website: str = Field(None, max_length=200)
    github: str = Field(None, max_length=100)
    twitter: str = Field(None, max_length=100)
    linkedin: str = Field(None, max_length=100)
    company: str = Field(None, max_length=100)
    job_title: str = Field(None, max_length=100)



class UserProfileStats(BaseModel):
    """Serializer for profile statistics.

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    total_profiles: int = ...
    profiles_with_company: int = ...
    profiles_with_social_links: int = ...
    most_active_users: list[dict[str, Any]] = ...



