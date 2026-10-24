"""
Support extension configuration.

Extend BaseExtensionSettings to customize behavior.
"""

from django_cfg.extensions.configs.apps import BaseExtensionSettings


class SupportSettings(BaseExtensionSettings):
    """Project-specific support settings."""

    name: str = "support"


settings = SupportSettings()
