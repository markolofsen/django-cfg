"""
Leads extension configuration.

Extend BaseExtensionSettings to customize behavior.
"""

from django_cfg.extensions.configs.apps import BaseExtensionSettings


class LeadsSettings(BaseExtensionSettings):
    """Project-specific leads settings."""

    name: str = "leads"
    # Override defaults here if needed
    # telegram_enabled: bool = False
    # email_enabled: bool = False


settings = LeadsSettings()
