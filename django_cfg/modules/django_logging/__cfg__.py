"""django_logging module configuration."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DjangoLoggingConfig(BaseModel):
    """
    Logging settings. Every field is read.

    Precedence: this config, then env (``DJANGO_CFG_LOG_DIR``,
    ``DJANGO_CFG_LOG_FORMAT``, ``DJANGO_CFG_LOG_LEVEL``), then default
    (stdout/stderr, text, WARNING or DEBUG with ``debug``).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def _drop_removed_fields(cls, data):
        """``enabled``, ``file_enabled`` and ``file_rotation_days`` were never read: accept and ignore."""
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

    level: Optional[Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]] = Field(
        default=None, description="Level of the django_cfg loggers"
    )
    format: Literal["text", "json"] = Field(default="text", description="json = one object per line")
    log_dir: Optional[str] = Field(
        default=None,
        description="Write log files here (WatchedFileHandler). None = stdout/stderr only",
    )


settings = DjangoLoggingConfig()

__all__ = ["DjangoLoggingConfig", "settings"]
