"""
Global configuration registry.

Manages current DjangoConfig instance for thread-safe access.
Extracted from original config.py for better organization.

Size: ~60 lines (simple state management)
"""

import threading
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..base.config_model import DjangoConfig

# Thread-local storage for current config
_thread_local = threading.local()

# Global config (fallback if thread-local not set)
_global_config: Optional["DjangoConfig"] = None


def get_current_config() -> Optional["DjangoConfig"]:
    """
    Get currently active DjangoConfig instance.

    Returns:
        Current config instance, or None if not set

    Example:
        >>> config = get_current_config()
        >>> if config:
        ...     print(config.project_name)
    """
    # Try thread-local first
    config = getattr(_thread_local, "config", None)
    if config is not None:
        return config

    # Fall back to global
    return _global_config


def set_current_config(config: "DjangoConfig") -> None:
    """
    Set currently active DjangoConfig instance.

    Args:
        config: DjangoConfig instance to set as current

    Example:
        >>> config = DjangoConfig(project_name="My Project", ...)
        >>> set_current_config(config)
    """
    global _global_config

    # Set both thread-local and global
    _thread_local.config = config
    _global_config = config


def clear_current_config() -> None:
    """
    Clear currently active config (useful for testing).

    Example:
        >>> clear_current_config()
        >>> assert get_current_config() is None
    """
    global _global_config

    # Clear both thread-local and global
    if hasattr(_thread_local, "config"):
        delattr(_thread_local, "config")

    _global_config = None


# Export functions
__all__ = [
    "get_current_config",
    "set_current_config",
    "clear_current_config",
]
