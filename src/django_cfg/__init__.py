"""
Django-CFG: Developer-First Django Configuration with Pydantic v2

A revolutionary Django configuration system that provides type-safe, intelligent,
and zero-boilerplate configuration management through Pydantic v2 models.

Key Features:
- 90% reduction in settings.py boilerplate
- 100% type safety with Pydantic v2 models
- Environment-aware smart defaults
- Seamless third-party integrations
- Zero raw dictionary usage

Example:
    ```python
    from django_cfg import DjangoConfig, DatabaseConnection
    
    class MyConfig(DjangoConfig):
        project_name: str = "My Project"
        databases: Dict[str, DatabaseConnection] = {
            "default": DatabaseConnection(
                engine="django.db.backends.postgresql",
                name="${DATABASE_URL:mydb}",
            )
        }
    
    config = MyConfig()
    ```
"""

# Configure Django app
default_app_config = "django_cfg.apps.DjangoCfgConfig"

from typing import TYPE_CHECKING

# Version information
__version__ = "1.1.11"
__author__ = "Unrealos Team"
__email__ = "info@unrealos.com"
__license__ = "MIT"

# Core exports - only import when needed to avoid circular imports
if TYPE_CHECKING:
    from django_cfg.core.config import DjangoConfig
    from django_cfg.models.database import DatabaseConnection, DatabaseRoutingRule
    from django_cfg.models.cache import CacheBackend
    from django_cfg.models.security import SecuritySettings
    from django_cfg.models.services import EmailConfig, TelegramConfig
    from django_cfg.models.jwt import JWTConfig
    from django_cfg.models.logging import LoggingConfig
    from django_cfg.models.third_party.revolution import RevolutionConfig, APIZone
    from django_cfg.models.unfold import UnfoldConfig, UnfoldColors, UnfoldSidebar
    from django_cfg.models.constance import ConstanceConfig, ConstanceField

    # Dashboard models are now part of unfold module
    from django_cfg.models.environment import EnvironmentConfig
    from django_cfg.exceptions import DjangoCfgException, ConfigurationError, ValidationError


# Lazy imports to avoid import time overhead
def __getattr__(name: str):
    """Lazy import mechanism to avoid circular imports and improve startup time."""

    # Core classes
    if name == "DjangoConfig":
        from django_cfg.core.config import DjangoConfig

        return DjangoConfig

    # Database models
    elif name == "DatabaseConnection":
        from django_cfg.models.database import DatabaseConnection

        return DatabaseConnection

    # Cache models
    elif name == "CacheBackend":
        from django_cfg.models.cache import CacheBackend

        return CacheBackend

    # Security models
    elif name == "SecuritySettings":
        from django_cfg.models.security import SecuritySettings

        return SecuritySettings

    # Service models
    elif name == "EmailConfig":
        from django_cfg.models.services import EmailConfig

        return EmailConfig
    elif name == "TelegramConfig":
        from django_cfg.models.services import TelegramConfig

        return TelegramConfig
    elif name == "JWTConfig":
        from django_cfg.models.jwt import JWTConfig

        return JWTConfig

    # Logging models
    elif name == "LoggingConfig":
        from django_cfg.models.logging import LoggingConfig

        return LoggingConfig

    # Third-party models - Django Revolution (always available)
    elif name == "RevolutionConfig":
        from django_cfg.models.revolution import RevolutionConfig

        return RevolutionConfig
    elif name == "APIZone":
        from django_revolution.config import ZoneModel as APIZone

        return APIZone
    elif name == "ZoneModel":
        from django_revolution.config import ZoneModel

        return ZoneModel
    elif name == "ZoneConfig":
        from django_revolution.app_config import ZoneConfig

        return ZoneConfig
    elif name == "DjangoRevolutionSettings":
        from django_revolution.config import DjangoRevolutionSettings

        return DjangoRevolutionSettings

    elif name == "UnfoldConfig":
        from django_cfg.models.unfold import UnfoldConfig

        return UnfoldConfig
    elif name == "UnfoldColors":
        from django_cfg.models.unfold import UnfoldColors

        return UnfoldColors
    elif name == "UnfoldSidebar":
        from django_cfg.models.unfold import UnfoldSidebar

        return UnfoldSidebar

    # Dashboard models
    elif name == "DashboardConfig":
        from django_cfg.models.unfold import DashboardWidget as DashboardConfig

        return DashboardConfig
    elif name == "QuickAction":
        from django_cfg.models.unfold import QuickAction

        return QuickAction
    elif name == "NavigationItem":
        from django_cfg.models.unfold import NavigationItem

        return NavigationItem
    elif name == "NavigationGroup":
        from django_cfg.models.unfold import NavigationGroup

        return NavigationGroup

    # Environment models
    elif name == "EnvironmentConfig":
        from django_cfg.models.environment import EnvironmentConfig

        return EnvironmentConfig

    # Exceptions
    elif name == "DjangoCfgException":
        from django_cfg.exceptions import DjangoCfgException

        return DjangoCfgException
    elif name == "ConfigurationError":
        from django_cfg.exceptions import ConfigurationError

        return ConfigurationError
    elif name == "ValidationError":
        from django_cfg.exceptions import ValidationError

        return ValidationError

    # Auto-configuring modules
    elif name == "DjangoLogger":
        from django_cfg.modules.django_logger import DjangoLogger

        return DjangoLogger
    elif name == "get_logger":
        from django_cfg.modules.django_logger import get_logger

        return get_logger
    elif name == "DjangoEmailService":
        from django_cfg.modules.django_email import DjangoEmailService

        return DjangoEmailService
    elif name == "send_email":
        from django_cfg.modules.django_email import send_email

        return send_email
    elif name == "DjangoTelegram":
        from django_cfg.modules.django_telegram import DjangoTelegram

        return DjangoTelegram
    elif name == "send_telegram_message":
        from django_cfg.modules.django_telegram import send_telegram_message

        return send_telegram_message
    elif name == "send_telegram_photo":
        from django_cfg.modules.django_telegram import send_telegram_photo

        return send_telegram_photo

    # Unfold models
    elif name == "UnfoldConfig":
        from django_cfg.models.unfold import UnfoldConfig

        return UnfoldConfig
    elif name == "UnfoldTheme":
        from django_cfg.models.unfold import UnfoldTheme

        return UnfoldTheme
    elif name == "UnfoldColors":
        from django_cfg.models.unfold import UnfoldColors

        return UnfoldColors
    elif name == "UnfoldSidebar":
        from django_cfg.models.unfold import UnfoldSidebar

        return UnfoldSidebar
    elif name == "NavigationItem":
        from django_cfg.models.unfold import NavigationItem

        return NavigationItem
    elif name == "NavigationGroup":
        from django_cfg.models.unfold import NavigationGroup

        return NavigationGroup
    elif name == "QuickAction":
        from django_cfg.models.unfold import QuickAction

        return QuickAction
    elif name == "DashboardWidget":
        from django_cfg.models.unfold import DashboardWidget

        return DashboardWidget
    elif name == "DropdownItem":
        from django_cfg.models.unfold import DropdownItem

        return DropdownItem

    # DRF models
    elif name == "DRFConfig":
        from django_cfg.models.drf import DRFConfig

        return DRFConfig
    elif name == "SpectacularConfig":
        from django_cfg.models.drf import SpectacularConfig

        return SpectacularConfig
    elif name == "SwaggerUISettings":
        from django_cfg.models.drf import SwaggerUISettings

        return SwaggerUISettings
    elif name == "RedocUISettings":
        from django_cfg.models.drf import RedocUISettings

        return RedocUISettings

    # Constance models
    elif name == "ConstanceConfig":
        from django_cfg.models.constance import ConstanceConfig

        return ConstanceConfig
    elif name == "ConstanceField":
        from django_cfg.models.constance import ConstanceField

        return ConstanceField

    # URL integration
    elif name == "add_django_cfg_urls":
        from django_cfg.integration import add_django_cfg_urls

        return add_django_cfg_urls
    elif name == "get_django_cfg_urls_info":
        from django_cfg.integration import get_django_cfg_urls_info

        return get_django_cfg_urls_info

    # Unknown attribute
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# Public API - what users can import
__all__ = [
    # Core
    "DjangoConfig",
    # Database
    "DatabaseConnection",
    # Cache
    "CacheBackend",
    # Security
    "SecuritySettings",
    # Services
    "EmailConfig",
    "TelegramConfig",
    "JWTConfig",
    # Logging
    "LoggingConfig",
    # Third-party integrations
    "RevolutionConfig",
    "APIZone",
    "UnfoldConfig",
    "UnfoldColors",
    "UnfoldSidebar",
    # Dashboard
    "DashboardConfig",
    "QuickAction",
    "NavigationItem",
    "NavigationGroup",
    # Environment
    "EnvironmentConfig",
    # Exceptions
    "DjangoCfgException",
    "ConfigurationError",
    "ValidationError",
    # Auto-configuring modules
    "DjangoLogger",
    "get_logger",
    "DjangoEmailService",
    "send_email",
    "DjangoTelegram",
    "send_telegram_message",
    "send_telegram_photo",
    # Unfold admin interface
    "UnfoldConfig",
    "UnfoldTheme",
    "UnfoldColors",
    "UnfoldSidebar",
    "NavigationItem",
    "NavigationGroup",
    "DropdownItem",
    "QuickAction",
    "DashboardWidget",
    # DRF
    "DRFConfig",
    "SpectacularConfig",
    "SwaggerUISettings",
    "RedocUISettings",
    # Constance
    "ConstanceConfig",
    "ConstanceField",
    # URL integration
    "add_django_cfg_urls",
    "get_django_cfg_urls_info",
]
