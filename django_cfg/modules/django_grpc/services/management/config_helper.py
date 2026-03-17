"""
django_grpc.services.management.config_helper — Single source of truth for gRPC config.

All gRPC module code should read environment and DjangoConfig values through this module
instead of calling get_current_config() / django.conf.settings directly.

Hierarchy:
  DjangoConfig (project config singleton)
    └─ .grpc_module → DjangoGrpcModuleConfig
         ├─ .server → GrpcServerConfig
         ├─ .auth   → GrpcAuthConfig
         └─ ...

Usage:
    from django_cfg.modules.django_grpc.services.management.config_helper import (
        get_grpc_module_config,
        is_development,
        get_secret_key,
        get_enable_reflection,
    )
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from django_cfg.utils import get_logger

if TYPE_CHECKING:
    from django_cfg.modules.django_grpc.__cfg__ import DjangoGrpcModuleConfig
    from django_cfg.modules.django_grpc.config.server import GrpcServerConfig

logger = get_logger("grpc.config")


# ---------------------------------------------------------------------------
# gRPC module config
# ---------------------------------------------------------------------------

def get_grpc_module_config() -> Optional["DjangoGrpcModuleConfig"]:
    """
    Return the DjangoGrpcModuleConfig from the current django-cfg singleton.

    Returns None if not configured or on any import/access error.
    This is the canonical accessor — all other helpers delegate to this.
    """
    try:
        from django_cfg.core.config import get_current_config
        from django_cfg.modules.django_grpc.__cfg__ import DjangoGrpcModuleConfig

        config = get_current_config()
        if not config:
            return None
        # grpc_module is a user-defined field on DjangoConfig — not in the base schema,
        # so getattr is intentional here (not a code smell).
        grpc_module = getattr(config, "grpc_module", None)
        if isinstance(grpc_module, DjangoGrpcModuleConfig):
            return grpc_module
    except Exception as e:
        logger.debug("get_grpc_module_config: %s", e)
    return None


def get_grpc_server_config() -> Optional["GrpcServerConfig"]:
    """Return GrpcServerConfig from grpc_module, or None."""
    cfg = get_grpc_module_config()
    return cfg.server if cfg else None


def is_grpc_enabled() -> bool:
    """Return True if grpc_module is configured and enabled."""
    cfg = get_grpc_module_config()
    return cfg.enabled if cfg else False


# ---------------------------------------------------------------------------
# DjangoConfig environment helpers
# Centralises all reads of DjangoConfig.is_development / debug / secret_key.
# Use these instead of accessing django.conf.settings or get_current_config() directly.
# ---------------------------------------------------------------------------

def _get_django_config():
    """Return the active DjangoConfig singleton, or None."""
    try:
        from django_cfg.core.config import get_current_config
        return get_current_config()
    except Exception:
        return None


def is_development() -> bool:
    """Return True if the project is running in development mode.

    Reads DjangoConfig.is_development. Falls back to True (safe default — better to
    show warnings than to silently suppress them in unknown environments).
    """
    cfg = _get_django_config()
    if cfg is not None:
        return bool(getattr(cfg, "is_development", False))
    # No config loaded → assume development (conservative: enable all diagnostics)
    return True


def is_production() -> bool:
    """Return True if the project is running in production mode."""
    cfg = _get_django_config()
    if cfg is not None:
        return bool(getattr(cfg, "is_production", False))
    return False


def get_debug_mode() -> bool:
    """Return True if DEBUG is enabled in DjangoConfig.

    Falls back to django.conf.settings.DEBUG if DjangoConfig is not yet loaded.
    """
    cfg = _get_django_config()
    if cfg is not None:
        return bool(getattr(cfg, "debug", False))
    # Fallback for early-startup contexts (before DjangoConfig is registered)
    try:
        from django.conf import settings as dj_settings
        return bool(getattr(dj_settings, "DEBUG", False))
    except Exception:
        return False


def get_secret_key() -> str:
    """Return the Django secret key from DjangoConfig.

    Preferred over reading django.conf.settings.SECRET_KEY directly — ensures all
    gRPC module code goes through the single config registry.
    """
    cfg = _get_django_config()
    if cfg is not None:
        key = getattr(cfg, "secret_key", None)
        if key:
            return str(key)
    # Fallback: django.conf.settings (always set by Django itself)
    from django.conf import settings as dj_settings
    return str(dj_settings.SECRET_KEY)


def get_root_urlconf() -> str:
    """Return ROOT_URLCONF from DjangoConfig or django.conf.settings."""
    cfg = _get_django_config()
    if cfg is not None:
        urlconf = getattr(cfg, "root_urlconf", None)
        if urlconf:
            return str(urlconf)
    from django.conf import settings as dj_settings
    return str(getattr(dj_settings, "ROOT_URLCONF", ""))


# ---------------------------------------------------------------------------
# Derived / smart-default helpers
# ---------------------------------------------------------------------------

def get_enable_reflection() -> bool:
    """Return the effective enable_reflection setting.

    Priority:
      1. GrpcServerConfig.enable_reflection (explicit user override)
      2. is_development() → True in dev, False in prod

    This means reflection is ON by default in development (for grpcurl) and OFF in
    production without any explicit config, which is the secure-by-default behaviour.
    """
    server_cfg = get_grpc_server_config()
    if server_cfg is not None:
        # If the user explicitly set the field in their DjangoConfig, respect it.
        # GrpcServerConfig.enable_reflection is always present (Pydantic field with default).
        # We treat it as an explicit override only when grpc_module is configured —
        # i.e. the user opted in to grpc at all, so their server config is intentional.
        return server_cfg.enable_reflection
    # No grpc_module configured → fall back to environment auto-detection
    return is_development()


__all__ = [
    # gRPC module
    "get_grpc_module_config",
    "get_grpc_server_config",
    "is_grpc_enabled",
    # DjangoConfig environment
    "is_development",
    "is_production",
    "get_debug_mode",
    "get_secret_key",
    "get_root_urlconf",
    # Derived
    "get_enable_reflection",
]
