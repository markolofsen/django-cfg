"""
Django-RQ Settings Generator.

Generates Django settings for django-rq task queue and scheduler.
Converts DjangoRQConfig Pydantic model to Django RQ_QUEUES and related settings.
"""

from typing import TYPE_CHECKING, Any, Dict, Optional

from ....models.django.django_rq import DjangoRQConfig

if TYPE_CHECKING:
    from ...base.config_model import DjangoConfig


class DjangoRQSettingsGenerator:
    """
    Settings generator for Django-RQ task queue.

    Converts DjangoRQConfig to Django settings:
    - RQ_QUEUES: Queue configurations
    - RQ_SHOW_ADMIN_LINK: Show link in admin
    - RQ_EXCEPTION_HANDLERS: Exception handlers
    - RQ_API_TOKEN: API authentication token

    Usage:
        >>> from django_cfg.models.django.django_rq import DjangoRQConfig
        >>> config = DjangoRQConfig(enabled=True)
        >>> generator = DjangoRQSettingsGenerator(config)
        >>> settings = generator.generate()
        >>> 'RQ_QUEUES' in settings
        True
    """

    def __init__(self, config: DjangoRQConfig, parent_config: Optional["DjangoConfig"] = None):
        """
        Initialize Django-RQ settings generator.

        Args:
            config: DjangoRQConfig instance
            parent_config: Parent DjangoConfig for accessing global settings like redis_url
        """
        self.config = config
        self.parent_config = parent_config

    def generate(self) -> Dict[str, Any]:
        """
        Generate Django-RQ settings.

        Returns:
            Dictionary with RQ_QUEUES and related configuration
        """
        if not self.config.enabled:
            return {}

        # Use the model's built-in to_django_settings method
        settings = self.config.to_django_settings(parent_config=self.parent_config)

        return settings

    def validate(self) -> None:
        """
        Validate Django-RQ configuration.

        Ensures:
        - At least 'default' queue exists (validated by Pydantic)
        - Queue names are unique (validated by Pydantic)
        - Queue configurations are valid

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.config.enabled:
            return

        # Validation is now handled by Pydantic field validators
        # This method is kept for potential custom validation logic


__all__ = ['DjangoRQSettingsGenerator']
