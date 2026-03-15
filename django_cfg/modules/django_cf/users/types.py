"""
django_cf.users.types — Pydantic models for user and project D1 sync.

Field names match D1 column names exactly so D1Q._extract() can pull
values directly from model_dump() without any manual to_params() method.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ProjectSyncData(BaseModel):
    """Typed model for the projects table row.

    Column order matches PROJECTS_TABLE — no manual to_params() needed.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    api_url:      str = Field(..., description="Project API URL — primary key")
    project_name: str = ""
    environment:  str = "production"
    synced_at:    str = Field(default_factory=_now_iso)

    @classmethod
    def from_django_config(cls, config: Any) -> "ProjectSyncData":
        environment = "development" if (
            hasattr(config, "is_development") and config.is_development
        ) else "production"
        return cls(
            api_url=str(config.api_url).rstrip("/"),
            project_name=getattr(config, "project_name", "") or "",
            environment=environment,
        )


class UserSyncData(BaseModel):
    """Typed model for the users table row.

    Column order matches USERS_TABLE — no manual to_params() needed.
    ``is_active`` is stored as INTEGER (0/1); the computed field
    ``is_active_int`` is excluded from model_dump() via exclude.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    id:          str = Field(..., description="User UUID — composite PK with api_url")
    api_url:     str = Field(..., description="Project API URL — composite PK")
    email:       str
    first_name:  str = ""
    last_name:   str = ""
    phone:       str = ""
    company:     str = ""
    position:    str = ""
    avatar:      str = ""
    is_active:   str = "1"      # stored as "0"/"1" — matches INTEGER column via str cast
    date_joined: str
    updated_at:  str
    synced_at:   str = Field(default_factory=_now_iso)

    @classmethod
    def from_user(cls, user: Any, api_url: str) -> "UserSyncData":
        now = _now_iso()
        updated_at = user.updated_at.isoformat() if getattr(user, "updated_at", None) else now
        date_joined = user.date_joined.isoformat() if getattr(user, "date_joined", None) else now

        avatar_url = ""
        if getattr(user, "avatar", None):
            try:
                avatar_url = user.avatar.url
            except Exception:
                avatar_url = str(user.avatar)

        phone    = str(getattr(user, "phone",    None) or "")
        company  = str(getattr(user, "company",  None) or "")
        position = str(getattr(user, "position", None) or "")

        return cls(
            id=str(user.pk),
            api_url=api_url.rstrip("/"),
            email=user.email,
            first_name=user.first_name or "",
            last_name=user.last_name or "",
            phone=phone,
            company=company,
            position=position,
            avatar=avatar_url,
            is_active="1" if user.is_active else "0",
            date_joined=date_joined,
            updated_at=updated_at,
        )


__all__ = ["ProjectSyncData", "UserSyncData"]
