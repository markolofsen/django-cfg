"""
Deprecated: ``LoggingConfig`` was never used by ``DjangoConfig``.

Kept for one release so downstream imports do not break. Logging is configured
by the generated ``LOGGING`` dict (``django_cfg.modules.django_logging.config``)
and ``DjangoConfig.logging`` (``DjangoLoggingConfig``). Removed in the next release.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class LoggingConfig(BaseModel):
    """Deprecated no-op shim. Use ``DjangoConfig.logging`` / ``DjangoLoggingConfig``."""

    model_config = ConfigDict(extra="allow")

    def __init__(self, **data: Any) -> None:
        from django_cfg.core.utils.runtime_paths import warn_once

        warn_once(
            "logging-config-shim",
            "django_cfg.LoggingConfig is deprecated, unused and will be removed in the next "
            "release. Use DjangoConfig(logging=DjangoLoggingConfig(...)) or DJANGO_CFG_LOG_DIR.",
        )
        super().__init__(**data)


__all__ = ["LoggingConfig"]
