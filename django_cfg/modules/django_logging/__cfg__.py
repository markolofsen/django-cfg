"""django_logging module configuration."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DjangoLoggingConfig(BaseModel):
    """Configuration for file-based logging."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    enabled: bool = True
    file_enabled: bool = Field(default=True, description="File logging (always on by default)")
    file_rotation_days: int = Field(default=30, ge=1, le=365)


settings = DjangoLoggingConfig()

__all__ = ["DjangoLoggingConfig", "settings"]
