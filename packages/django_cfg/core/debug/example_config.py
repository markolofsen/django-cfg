"""
Example configuration with debug_warnings enabled.

This shows how to enable warnings traceback through DjangoConfig.
"""

from django_cfg import DjangoConfig, DatabaseConfig


class DebugConfig(DjangoConfig):
    """
    Example configuration with warnings debug enabled.

    Usage:
        # In your settings.py or config.py
        from path.to.config import DebugConfig

        config = DebugConfig()
        settings = config.get_all_settings()
    """

    # Project basics
    project_name: str = "Debug Example"
    secret_key: str = "django-insecure-example-key-change-in-production"

    # Enable debug mode for development
    debug: bool = True

    # Enable warnings traceback for debugging
    # This will show full stack trace for RuntimeWarnings about:
    # - Database access during app initialization
    # - APPS_NOT_READY warnings
    # - Other app initialization issues
    debug_warnings: bool = True

    # Database configuration
    databases: dict[str, DatabaseConfig] = {
        "default": DatabaseConfig(
            engine="django.db.backends.sqlite3",
            name=":memory:",
        )
    }


# Alternative: Enable only in development
class SmartDebugConfig(DjangoConfig):
    """Automatically enable debug_warnings in development mode."""

    project_name: str = "Smart Debug Example"
    secret_key: str = "django-insecure-example-key"

    # Auto-enable debug_warnings in development
    @property
    def debug_warnings(self) -> bool:
        """Enable warnings debug only in development."""
        return self.env_mode.is_development

    databases: dict[str, DatabaseConfig] = {
        "default": DatabaseConfig(
            engine="django.db.backends.sqlite3",
            name=":memory:",
        )
    }
