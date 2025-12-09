"""
Core Django settings generator.

Generates fundamental Django settings like SECRET_KEY, DEBUG, INSTALLED_APPS, etc.
Size: ~120 lines (focused on core settings)
"""

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from ...base.config_model import DjangoConfig


class CoreSettingsGenerator:
    """
    Generates core Django settings.

    Responsibilities:
    - SECRET_KEY, DEBUG
    - INSTALLED_APPS (via config.get_installed_apps())
    - MIDDLEWARE (via config.get_middleware())
    - ALLOWED_HOSTS (via config.get_allowed_hosts())
    - ROOT_URLCONF, WSGI_APPLICATION
    - AUTH_USER_MODEL
    - BASE_DIR
    - DEFAULT_AUTO_FIELD

    Example:
        ```python
        generator = CoreSettingsGenerator(config)
        settings = generator.generate()
        ```
    """

    def __init__(self, config: "DjangoConfig"):
        """
        Initialize generator with configuration.

        Args:
            config: DjangoConfig instance
        """
        self.config = config

    def generate(self) -> Dict[str, Any]:
        """
        Generate core Django settings.

        Returns:
            Dictionary with core Django settings

        Example:
            >>> config = DjangoConfig(project_name="Test", secret_key="x"*50)
            >>> generator = CoreSettingsGenerator(config)
            >>> settings = generator.generate()
            >>> "SECRET_KEY" in settings
            True
        """
        settings = {
            "SECRET_KEY": self.config.secret_key,
            "DEBUG": self.config.debug,
            "ALLOWED_HOSTS": self.config.get_allowed_hosts(),
            "INSTALLED_APPS": self.config.get_installed_apps(),
            "MIDDLEWARE": self.config.get_middleware(),
        }

        # Add URL configuration
        if self.config.root_urlconf:
            settings["ROOT_URLCONF"] = self.config.root_urlconf

        if self.config.wsgi_application:
            settings["WSGI_APPLICATION"] = self.config.wsgi_application

        # Add custom user model - always use django-cfg accounts
        # accounts is always enabled - core django-cfg functionality
        settings["AUTH_USER_MODEL"] = "django_cfg_accounts.CustomUser"

        # Add base directory (always set, auto-detects from manage.py location)
        settings["BASE_DIR"] = self.config.base_dir

        # Add default auto field
        settings["DEFAULT_AUTO_FIELD"] = "django.db.models.BigAutoField"

        return settings


__all__ = ["CoreSettingsGenerator"]
