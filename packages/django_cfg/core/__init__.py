"""
Django-CFG Core Module

Refactored modular architecture:
- base/ - Core config models
- types/ - Type definitions and enums
- builders/ - Settings builders (apps, middleware, security)
- services/ - Orchestration services
- state/ - Global state management
- integration/ - Integration utilities (version, startup info, URLs)
- constants.py - Default configurations

Public API:
    from django_cfg.core import DjangoConfig
    from django_cfg.core import EnvironmentMode, StartupInfoMode
"""

# Main exports for convenient access
from .base import DjangoConfig
from .types import EnvironmentMode, StartupInfoMode
from .state import get_current_config, set_current_config, clear_current_config
from .constants import DEFAULT_APPS, DEFAULT_MIDDLEWARE

# Integration utilities
from .integration import (
    print_startup_info,
    print_ngrok_tunnel_info,
    get_version_info,
    get_latest_version,
    get_current_version,
    get_all_commands,
    get_command_count,
    get_commands_with_descriptions,
    add_django_cfg_urls,
    get_django_cfg_urls_info,
)

# Validation
from .validation import ConfigurationValidator

# Export all for public API
__all__ = [
    # Main config
    "DjangoConfig",
    # Types
    "EnvironmentMode",
    "StartupInfoMode",
    # Constants
    "DEFAULT_APPS",
    "DEFAULT_MIDDLEWARE",
    # Global state
    "get_current_config",
    "set_current_config",
    "clear_current_config",
    # Integration utilities
    "print_startup_info",
    "print_ngrok_tunnel_info",
    "get_version_info",
    "get_latest_version",
    "get_current_version",
    "get_all_commands",
    "get_command_count",
    "get_commands_with_descriptions",
    "add_django_cfg_urls",
    "get_django_cfg_urls_info",
    # Validation
    "ConfigurationValidator",
]
