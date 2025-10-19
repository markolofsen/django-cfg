"""
Application limits settings generator.

Handles request limits and rate limiting configuration.
Size: ~50 lines (focused on limits settings)
"""

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from ...base.config_model import DjangoConfig


class LimitsSettingsGenerator:
    """
    Generates application limits settings.

    Responsibilities:
    - DATA_UPLOAD_MAX_MEMORY_SIZE
    - FILE_UPLOAD_MAX_MEMORY_SIZE
    - Rate limiting configuration

    Example:
        ```python
        generator = LimitsSettingsGenerator(config)
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
        Generate limits settings.

        Returns:
            Dictionary with limits configuration

        Example:
            >>> generator = LimitsSettingsGenerator(config)
            >>> settings = generator.generate()
        """
        if not self.config.limits:
            return {}

        limits_settings = self.config.limits.to_django_settings()

        return limits_settings


__all__ = ["LimitsSettingsGenerator"]
