"""
Newsletter extension configuration.

Extend BaseExtensionSettings to customize behavior.
"""

from django_cfg.extensions.configs.apps import BaseExtensionSettings


class NewsletterSettings(BaseExtensionSettings):
    """Project-specific newsletter settings."""

    name: str = "newsletter"


settings = NewsletterSettings()
