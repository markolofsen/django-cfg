"""
Email settings generator.

Handles Django email configuration.
Size: ~50 lines (focused on email settings)
"""

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from ...base.config_model import DjangoConfig


class EmailSettingsGenerator:
    """
    Generates email settings.

    Responsibilities:
    - EMAIL_BACKEND configuration
    - SMTP settings
    - Email authentication

    Example:
        ```python
        generator = EmailSettingsGenerator(config)
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
        Generate email settings.

        Returns:
            Dictionary with email configuration

        Example:
            >>> generator = EmailSettingsGenerator(config)
            >>> settings = generator.generate()
        """
        if not self.config.email:
            return {}

        email_settings = self.config.email.to_django_settings()

        return email_settings


__all__ = ["EmailSettingsGenerator"]
