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
from .agents import BaseAgentsSettings
from .backup import BaseBackupSettings
from .currency import BaseCurrencySettings
from .knowbase import BaseKnowbaseSettings
from .leads import BaseLeadsSettings
from .maintenance import BaseMaintenanceSettings
from .newsletter import BaseNewsletterSettings
from .payments import BasePaymentsSettings
from .support import BaseSupportSettings

__all__ = [
    "APP_LABEL_PREFIX",
    "BaseExtensionSettings",
    "ExtensionScheduleConfig",
    "NavigationItem",
    "NavigationSection",
    "BaseAgentsSettings",
    "BaseBackupSettings",
    "BaseCurrencySettings",
    "BaseKnowbaseSettings",
    "BaseLeadsSettings",
    "BaseMaintenanceSettings",
    "BaseNewsletterSettings",
    "BasePaymentsSettings",
    "BaseSupportSettings",
]
