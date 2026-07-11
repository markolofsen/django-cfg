"""
django_centrifugo — Centrifugo module for django-cfg.

All Centrifugo logic lives here:
- Services: CentrifugoClient (httpx publish)
- Management commands: centrifugo_publish, generate_centrifugo_clients
- Code generation: multi-language client generators

Public API:
    from django_cfg.modules.django_centrifugo import get_client, is_enabled
    from django_cfg.modules.django_centrifugo.services.token_generator import generate_centrifugo_token
"""

from __future__ import annotations

default_app_config = "django_cfg.modules.django_centrifugo.apps.DjangoCentrifugoConfig"

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .services.client.client import CentrifugoClient

from .exceptions import DjangoCentrifugoConfigError, DjangoCentrifugoError, DjangoCentrifugoSyncError

_client_instance: Optional["CentrifugoClient"] = None


def is_enabled() -> bool:
    """Return True when Centrifugo is configured on DjangoConfig."""
    try:
        from .services.config_helper import get_centrifugo_config
        return get_centrifugo_config() is not None
    except Exception:
        return False


def get_client() -> "CentrifugoClient":
    """Return (cached) CentrifugoClient instance.

    Raises DjangoCentrifugoConfigError if centrifugo is not configured.
    """
    global _client_instance
    if _client_instance is None:
        from .services.config_helper import get_centrifugo_config
        from .services.client.client import CentrifugoClient
        cfg = get_centrifugo_config()
        _client_instance = CentrifugoClient(config=cfg)
    return _client_instance


def get_centrifugo_config():
    """Return the active CentrifugoConfig instance."""
    from .services.config_helper import get_centrifugo_config
    return get_centrifugo_config()


def reset_client() -> None:
    """Reset cached client instance (useful in tests)."""
    global _client_instance
    _client_instance = None


__all__ = [
    # Exceptions
    "DjangoCentrifugoError",
    "DjangoCentrifugoConfigError",
    "DjangoCentrifugoSyncError",
    # Helpers
    "is_enabled",
    "get_client",
    "get_centrifugo_config",
    "reset_client",
]
