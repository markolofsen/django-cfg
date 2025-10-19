"""
Logging settings generator.

Handles Django logging configuration.
Size: ~60 lines (focused on logging settings)
"""

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from ...base.config_model import DjangoConfig


class LoggingSettingsGenerator:
    """
    Generates logging settings.

    Responsibilities:
    - LOGGING configuration
    - Environment-specific log levels
    - Log handlers and formatters

    Example:
        ```python
        generator = LoggingSettingsGenerator(config)
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
        Generate logging settings.

        Returns:
            Dictionary with logging configuration

        Example:
            >>> generator = LoggingSettingsGenerator(config)
            >>> settings = generator.generate()
            >>> "LOGGING" in settings
            True
        """
        from ....utils.smart_defaults import SmartDefaults

        # Generate logging defaults based on environment
        logging_defaults = SmartDefaults.get_logging_defaults(
            self.config.env_mode,
            self.config.debug
        )

        if not logging_defaults:
            return {}

        return {"LOGGING": logging_defaults}


__all__ = ["LoggingSettingsGenerator"]
