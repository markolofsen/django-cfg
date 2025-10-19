"""
Tailwind CSS settings generator for django-cfg.

Generates Django settings for django-tailwind integration.
"""

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from django_cfg.core.base.config_model import DjangoConfig


class TailwindSettingsGenerator:
    """
    Generates Django settings for Tailwind CSS integration.

    Responsibilities:
    - Add Tailwind-specific Django settings
    - Configure TAILWIND_APP_NAME

    Example:
        ```python
        generator = TailwindSettingsGenerator(config)
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
        Generate Tailwind CSS settings.

        Returns:
            Dictionary with Tailwind-specific settings
        """
        settings = {}

        # Tailwind is always enabled - add app name setting
        settings["TAILWIND_APP_NAME"] = self.config.tailwind_app_name

        return settings


__all__ = [
    "TailwindSettingsGenerator",
]
