"""Global state management for django-cfg."""

from .registry import clear_current_config, get_current_config, set_current_config

__all__ = [
    "get_current_config",
    "set_current_config",
    "clear_current_config",
]
