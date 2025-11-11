"""
Internationalization settings generator.

Handles Django i18n/l10n configuration.
Size: ~60 lines (focused on i18n settings)
"""

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from ...base.config_model import DjangoConfig


class I18nSettingsGenerator:
    """
    Generates internationalization settings.

    Responsibilities:
    - LANGUAGE_CODE, TIME_ZONE
    - USE_I18N, USE_TZ flags
    - Localization settings

    Example:
        ```python
        generator = I18nSettingsGenerator(config)
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
        Generate i18n settings.

        Returns:
            Dictionary with i18n configuration

        Example:
            >>> generator = I18nSettingsGenerator(config)
            >>> settings = generator.generate()
            >>> "LANGUAGE_CODE" in settings
            True
        """
        settings = {
            "LANGUAGE_CODE": "en-us",
            "TIME_ZONE": "UTC",
            "USE_I18N": True,
            "USE_TZ": True,
        }

        # Adjust for different environments
        if self.config.is_development:
            settings["USE_L10N"] = True  # Deprecated but sometimes needed

        return settings


__all__ = ["I18nSettingsGenerator"]
