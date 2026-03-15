"""
Base configuration classes for extension apps.

All extension settings should inherit from BaseExtensionSettings.
"""

from .constants import APP_LABEL_PREFIX
from .navigation import NavigationItem, NavigationSection
from .schedule import ExtensionScheduleConfig
from .settings import BaseExtensionSettings

__all__ = [
    "APP_LABEL_PREFIX",
    "BaseExtensionSettings",
    "ExtensionScheduleConfig",
    "NavigationItem",
    "NavigationSection",
]
