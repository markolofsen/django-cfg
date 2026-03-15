"""
Convenience re-exports for django-cfg core.

Usage:
    from django_cfg.core.config import DjangoConfig, EnvironmentMode
"""

from .base.config_model import DjangoConfig
from .constants import DEFAULT_APPS, DEFAULT_MIDDLEWARE
from .state.registry import (
    clear_current_config,
    get_current_config,
    set_current_config,
)
from .types.enums import EnvironmentMode, StartupInfoMode

# Public API
__all__ = [
    # Main config
    "DjangoConfig",
    # Enums
    "EnvironmentMode",
    "StartupInfoMode",
    # Constants
    "DEFAULT_APPS",
    "DEFAULT_MIDDLEWARE",
    # Global state
    "get_current_config",
    "set_current_config",
    "clear_current_config",
]
