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
from .constants import DEFAULT_APPS, DEFAULT_MIDDLEWARE
from .middleware import PublicAPICORSMiddleware

# Integration utilities
from .integration import (
    add_django_cfg_urls,
    get_all_commands,
    get_command_count,
    get_commands_with_descriptions,
    get_current_version,
    get_django_cfg_urls_info,
    get_latest_version,
    get_version_info,
    print_ngrok_tunnel_info,
    print_startup_info,
)
from .state import clear_current_config, get_current_config, set_current_config
from .types import EnvironmentMode, StartupInfoMode

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
    # Middleware
    "PublicAPICORSMiddleware",
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
