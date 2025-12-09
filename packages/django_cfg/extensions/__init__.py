"""
Django-CFG Extensions System

Auto-discovers and loads extensions from the user's project.
Extensions are placed in extensions/ folder and work as-is.

Usage:
    # In your extension's __cfg__.py:
    from django_cfg.extensions.configs.apps.leads import BaseLeadsSettings

    class LeadsSettings(BaseLeadsSettings):
        telegram_enabled: bool = False  # override defaults

    settings = LeadsSettings()

Project Structure:
    your_project/
    └── extensions/
        ├── apps/           # Django apps with models
        │   └── leads/
        │       ├── __cfg__.py   # Required: settings = LeadsSettings()
        │       ├── apps.py
        │       ├── models.py
        │       ├── admin.py
        │       ├── urls.py      # Main API: /cfg/leads/
        │       ├── urls_admin.py # Admin API: /cfg/leads/admin/
        │       └── ...
        └── modules/        # Utility modules (no models)
            └── analytics/

URL Convention:
    - urls.py -> /cfg/{prefix}/ (main API)
    - urls_admin.py -> /cfg/{prefix}/admin/ (admin API)
    - urls_system.py -> /cfg/{prefix}/system/ (system API)
    - urls_<name>.py -> /cfg/{prefix}/<name>/ (custom suffix)
"""

from .configs.apps.base import (
    BaseExtensionSettings,
    NavigationItem,
    NavigationSection,
)
from .configs.apps import BaseCurrencySettings
from .configs.modules import BaseModuleSettings
from .scanner import DiscoveredExtension, ExtensionScanner
from .loader import ExtensionLoader, get_extension_loader
from .module_loader import ModuleLoader, get_module_loader, requires_module
from .mixin import ExtensionMixin, get_extension_helper
from .urls import discover_url_modules, get_extension_url_patterns
from .constance import get_extension_constance_fields
from .schedules import get_extension_schedules

__all__ = [
    # Base settings for apps
    "BaseExtensionSettings",
    "NavigationItem",
    "NavigationSection",
    # Base settings for modules
    "BaseModuleSettings",
    "BaseCurrencySettings",
    # App Discovery
    "ExtensionScanner",
    "DiscoveredExtension",
    "ExtensionLoader",
    "get_extension_loader",
    # Module Discovery
    "ModuleLoader",
    "get_module_loader",
    "requires_module",
    # URL discovery
    "discover_url_modules",
    "get_extension_url_patterns",
    # Constance fields discovery
    "get_extension_constance_fields",
    # RQ schedules discovery
    "get_extension_schedules",
    # Mixin for BaseCfgModule
    "ExtensionMixin",
    "get_extension_helper",
]
