"""
Base configuration for leads extension.

Users extend this class in their extension's __cfg__.py:

    from django_cfg.extensions.configs.apps.leads import BaseLeadsSettings

    class LeadsSettings(BaseLeadsSettings):
        telegram_enabled: bool = False  # Override default

    settings = LeadsSettings()
"""

from pydantic import Field

from django_cfg.modules.django_admin.icons import Icons

from .base import BaseExtensionSettings, NavigationItem, NavigationSection


class BaseLeadsSettings(BaseExtensionSettings):
    """Base settings for leads extension."""

    # === Manifest defaults ===
    name: str = "leads"
    version: str = "1.0.0"
    description: str = "Lead management and contact forms"
    author: str = "DjangoCFG Team"
    min_djangocfg_version: str = "1.5.0"
    django_app_label: str = "leads"
    url_prefix: str = "leads"
    url_namespace: str = "leads"

    # === Notifications ===
    telegram_enabled: bool = Field(
        default=True,
        description="Send Telegram notifications for new leads"
    )
    email_enabled: bool = Field(
        default=True,
        description="Send Email notifications for new leads"
    )

    # === Email settings ===
    email_template: str = Field(
        default="emails/base_email",
        description="Email template name for lead notifications"
    )
    email_subject_prefix: str = Field(
        default="New Lead:",
        description="Prefix for email notification subject"
    )

    # === Telegram settings ===
    telegram_success_title: str = Field(
        default="New lead from {site_url}",
        description="Telegram message title template. Available: {site_url}, {name}, {email}"
    )
    telegram_message_max_length: int = Field(
        default=200,
        description="Max length for message preview in Telegram"
    )

    # === Admin Navigation ===
    navigation: NavigationSection = Field(
        default_factory=lambda: NavigationSection(
            title="Leads",
            icon=Icons.CONTACT_PAGE,
            collapsible=True,
            items=[
                NavigationItem(
                    title="All Leads",
                    icon=Icons.CONTACT_PAGE,
                    app="leads",
                    model="lead",
                ),
            ],
        ),
        description="Admin navigation section configuration"
    )
