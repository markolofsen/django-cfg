"""
Centrifugo Config Helper.

Utility functions for accessing Centrifugo configuration from django-cfg.
"""

from typing import Optional

from django_cfg.utils import get_logger

logger = get_logger("centrifugo.config")


def get_centrifugo_config():
    """
    Get Centrifugo configuration from django-cfg global state.

    Returns:
        DjangoCfgCentrifugoConfig instance or None if not configured

    Example:
        >>> config = get_centrifugo_config()
        >>> if config:
        ...     print(config.wrapper_url)
    """
    from django_cfg.core import get_current_config

    # Try to get config from django-cfg global state
    django_cfg_config = get_current_config()

    if django_cfg_config and hasattr(django_cfg_config, "centrifugo") and django_cfg_config.centrifugo:
        return django_cfg_config.centrifugo

    return None


def get_centrifugo_config_or_default():
    """
    Get Centrifugo configuration from django-cfg or return default.

    Returns:
        DjangoCfgCentrifugoConfig instance (always)

    Example:
        >>> config = get_centrifugo_config_or_default()
        >>> print(config.wrapper_url)  # Always works, fallback to default
    """
    config = get_centrifugo_config()

    if config:
        return config

    # Fallback to default config
    from ..client.config import DjangoCfgCentrifugoConfig

    logger.warning("Django-CFG centrifugo config not found, using default config")
    return DjangoCfgCentrifugoConfig()


__all__ = [
    "get_centrifugo_config",
    "get_centrifugo_config_or_default",
]
