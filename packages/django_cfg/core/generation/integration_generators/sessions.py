"""
Session settings generator.

Handles Django session configuration.
Size: ~60 lines (focused on session settings)
"""

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from ...base.config_model import DjangoConfig


class SessionSettingsGenerator:
    """
    Generates Django session settings.

    Responsibilities:
    - Configure session backend (database/cache)
    - Set session cookie parameters
    - Session timeout and security

    Example:
        ```python
        generator = SessionSettingsGenerator(config)
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
        Generate session settings.

        Returns:
            Dictionary with session configuration

        Example:
            >>> generator = SessionSettingsGenerator(config)
            >>> settings = generator.generate()
            >>> "SESSION_ENGINE" in settings
            True
        """
        # Default session configuration - use database for persistence
        settings = {
            "SESSION_ENGINE": "django.contrib.sessions.backends.db",
            "SESSION_COOKIE_AGE": 86400 * 7,  # 7 days
            "SESSION_SAVE_EVERY_REQUEST": True,
        }

        # Note: If cache_sessions is configured, CacheSettingsGenerator will override
        # SESSION_ENGINE to use cache backend

        return settings


__all__ = ["SessionSettingsGenerator"]
