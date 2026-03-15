"""
django_cf — Cloudflare integration module for django-cfg.

Provides automatic user sync to Cloudflare D1 (SQLite at edge).

Usage in djangoconfig.py:
    from django_cfg.modules.django_cf import CloudflareConfig

    class MyConfig(DjangoConfig):
        cloudflare: CloudflareConfig = CloudflareConfig(
            enabled=True,
            account_id="${CF_ACCOUNT_ID}",
            api_token="${CF_API_TOKEN}",
            d1_database_id="${CF_D1_DATABASE_ID}",
        )

Module auto-wires post_save → RQ task → D1 upsert when enabled.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .users.service import UserSyncService

default_app_config = "django_cfg.modules.django_cf.apps.DjangoCfConfig"

from .__cfg__ import CloudflareConfig
from .exceptions import (
    CloudflareConfigError,
    CloudflareError,
    CloudflareQueryError,
    CloudflareSchemaError,
)
from .core.types import D1QueryResult
from .users.types import UserSyncData

# ─────────────────────────────────────────────────────────────────────────────
# Module-level helpers
# ─────────────────────────────────────────────────────────────────────────────

_service_instance: Optional["UserSyncService"] = None


def _get_config() -> Optional[CloudflareConfig]:
    """Auto-discover CloudflareConfig from live DjangoConfig."""
    try:
        from django_cfg.core.state.registry import get_current_config
        cfg = get_current_config()
        if cfg and hasattr(cfg, "cloudflare"):
            return cfg.cloudflare  # type: ignore[return-value]
    except Exception:
        pass
    return None


def is_ready() -> bool:
    """Return True when module is enabled and credentials are set."""
    config = _get_config()
    return config is not None and config.is_ready()


def get_service() -> "UserSyncService":
    """Return (cached) UserSyncService instance.

    Raises CloudflareConfigError if module is not ready.
    """
    global _service_instance
    if _service_instance is None:
        config = _get_config()
        if config is None or not config.is_ready():
            raise CloudflareConfigError(
                "django_cf: module not configured — add CloudflareConfig to DjangoConfig"
            )
        from .users.service import UserSyncService
        _service_instance = UserSyncService()
    return _service_instance


def reset_service() -> None:
    """Reset cached service instance (useful in tests)."""
    global _service_instance
    _service_instance = None


__all__ = [
    # Config
    "CloudflareConfig",
    # Exceptions
    "CloudflareError",
    "CloudflareConfigError",
    "CloudflareQueryError",
    "CloudflareSchemaError",
    # Types
    "UserSyncData",
    "D1QueryResult",
    # Helpers
    "is_ready",
    "get_service",
    "reset_service",
]
