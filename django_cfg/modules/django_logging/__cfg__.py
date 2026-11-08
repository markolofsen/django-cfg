"""django_logging module configuration."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DjangoLoggingConfig(BaseModel):
    """
    The ``logging`` block of ``DjangoConfig``.

    Precedence for every field: this config, then the env var named below, then the
    built-in default. General logs are stdout JSON with no files; the monitor-event
    logger has its own small rotating file (see ``dir``).

    ``DjangoConfig(logging=DjangoLoggingConfig(dir="/var/log/app", rotate_mb=10))``
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def _drop_removed_fields(cls, data):
        """Fields removed in earlier releases are accepted and ignored with one warning."""
        if isinstance(data, dict):
            removed = {"enabled", "file_enabled", "file_rotation_days"} & set(data)
            if removed:
                from django_cfg.core.utils.runtime_paths import warn_once

                warn_once(
                    "logging-cfg-removed-fields",
                    f"DjangoLoggingConfig fields {sorted(removed)} are removed and ignored.",
                )
                data = {k: v for k, v in data.items() if k not in removed}
        return data

    dir: Optional[str] = Field(
        default=None,
        description=(
            "Log directory (env DJANGO_CFG_LOG_DIR). Setting it adds django.log next to the monitor "
            "file. None: no general log file; the monitor file goes to /var/log/<app> if writable, "
            "else the per-user state dir, else stdout only (one warning). Never inside the project "
            "tree by default."
        ),
    )
    level: Optional[Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]] = Field(
        default=None, description="Level of the django_cfg loggers (env DJANGO_CFG_LOG_LEVEL)"
    )
    format: Optional[Literal["text", "json"]] = Field(
        default=None,
        description="json = one object per line. None = json when stderr is not a terminal, text at a terminal (env DJANGO_CFG_LOG_FORMAT)",
    )
    rotate_mb: Optional[int] = Field(
        default=None, ge=0,
        description="Rotate a log file at this size in MB; 0 = never (leave it to logrotate). Default 10 (env DJANGO_CFG_LOG_ROTATE_MB)",
    )
    backups: Optional[int] = Field(
        default=None, ge=0, description="Rotated files kept per log. Default 5 (env DJANGO_CFG_LOG_BACKUPS)"
    )
    retain_days: Optional[int] = Field(
        default=None, ge=0,
        description="Boot prune deletes rotated django-cfg files older than this. Default 14; 0 = by count and size only (env DJANGO_CFG_LOG_RETAIN_DAYS)",
    )


settings = DjangoLoggingConfig()

__all__ = ["DjangoLoggingConfig", "settings"]
