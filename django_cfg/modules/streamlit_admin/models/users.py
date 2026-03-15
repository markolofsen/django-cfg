"""User UI models for Streamlit admin.

User profile and account presentation models.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserInfo(BaseModel):
    """Basic user information for lists."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    id: str
    email: str
    username: str | None = None
    display_name: str | None = None
    is_active: bool = True


class UserProfile(BaseModel):
    """Full user profile for display."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    id: str
    email: str
    username: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    is_staff: bool = False
    is_superuser: bool = False
    date_joined: datetime | None = None
    last_login: datetime | None = None
