"""
Base configuration classes for extension apps.

Each app extension has a corresponding base settings class here.
"""

from .base import (
    APP_LABEL_PREFIX,
    BaseExtensionSettings,
    ExtensionScheduleConfig,
    NavigationItem,
    NavigationSection,
)
from .currency import BaseCurrencySettings

__all__ = [
    "APP_LABEL_PREFIX",
    "BaseExtensionSettings",
    "ExtensionScheduleConfig",
    "NavigationItem",
    "NavigationSection",
    "BaseCurrencySettings",
]
