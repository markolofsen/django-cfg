"""
django_centrifugo — Centrifugo module for django-cfg.

Full replacement for apps/integrations/centrifugo/. All Centrifugo logic lives here:
- Services: CentrifugoClient (httpx publish), CentrifugoLogger (D1-backed log)
- D1 persistence: publish history via centrifugo_logs append-only table
- Management commands: create_centrifugo_d1_schema, centrifugo_publish, generate_centrifugo_clients
- Streamlit dashboard: Centrifugo Overview, Publishes, Channels
- Code generation: multi-language client generators

Data storage:
- D1     — publish history (centrifugo_logs)

No PostgreSQL used.

Public API:
    from django_cfg.modules.django_centrifugo import get_client, is_enabled
    from django_cfg.modules.django_centrifugo.services.logging import CentrifugoLogger
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
    """Return True when django_cf is configured and ready."""
    try:
        from django_cfg.modules.django_cf import is_ready
        return is_ready()
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
