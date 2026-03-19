"""django_logging module configuration."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DjangoLoggingConfig(BaseModel):
    """Configuration for D1-backed logging persistence."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    enabled: bool = True
    d1_enabled: bool = Field(default=True, description="Enable D1 persistence (auto-enables when CloudflareConfig is ready)")
    d1_min_level: str = Field(default="WARNING", description="Minimum level for D1 (WARNING/ERROR/CRITICAL)")
    file_enabled: bool = Field(default=True, description="File logging (always on by default)")
    file_rotation_days: int = Field(default=30, ge=1, le=365)
    telegram_alerts_enabled: bool = False
    cleanup_days: int = Field(default=90, ge=1, le=365, description="D1 event TTL in days")
    normalization_enabled: bool = Field(default=True, description="Strip dynamic data before fingerprinting")


settings = DjangoLoggingConfig()

__all__ = ["DjangoLoggingConfig", "settings"]
