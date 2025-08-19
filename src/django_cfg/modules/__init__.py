"""
Django CFG Modules

Auto-configuring utility modules that integrate seamlessly with DjangoConfig.
All modules automatically receive configuration from the DjangoConfig instance
without requiring manual parameter passing.
"""

from typing import TYPE_CHECKING, Optional, Any
import importlib
import os

if TYPE_CHECKING:
    from django_cfg.core.config import DjangoConfig


class BaseModule:
    """
    Base class for auto-configuring django_cfg modules.

    All modules inherit from this to automatically receive
    configuration from the DjangoConfig instance.
    """

    _config_instance: Optional["DjangoConfig"] = None

    @classmethod
    def get_config(cls) -> "DjangoConfig":
        """Get the DjangoConfig instance automatically."""
        if cls._config_instance is None:
            cls._config_instance = cls._discover_config()
        return cls._config_instance

    @classmethod
    def _discover_config(cls) -> "DjangoConfig":
        """Discover the DjangoConfig instance from Django settings."""
        try:
            # Try to get config from Django settings module
            settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")
            if settings_module:
                settings_mod = importlib.import_module(settings_module)
                if hasattr(settings_mod, "config"):
                    return settings_mod.config

            # Fallback: try to create minimal config from Django settings
            from django.conf import settings
            from django_cfg import DjangoConfig

            return DjangoConfig(
                project_name=getattr(settings, "PROJECT_NAME", "Django Project"),
                secret_key=settings.SECRET_KEY,
                debug=settings.DEBUG,
                allowed_hosts=settings.ALLOWED_HOSTS,
            )

        except Exception as e:
            raise RuntimeError(f"Could not discover DjangoConfig instance: {e}")

    @classmethod
    def reset_config(cls):
        """Reset the cached config instance (useful for testing)."""
        cls._config_instance = None


# Export the base module
__all__ = ["BaseModule"]
