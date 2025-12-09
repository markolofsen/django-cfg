"""
Base configuration for support extension.

Users extend this class in their extension's __cfg__.py:

    from django_cfg.extensions.configs.apps.support import BaseSupportSettings

    class SupportSettings(BaseSupportSettings):
        telegram_enabled: bool = False  # Override default

    settings = SupportSettings()
"""

from pydantic import Field

from django_cfg.modules.django_admin.icons import Icons

from .base import BaseExtensionSettings, NavigationItem, NavigationSection


class BaseSupportSettings(BaseExtensionSettings):
    """Base settings for support extension."""

    # === Manifest defaults ===
    name: str = "support"
    version: str = "1.0.0"
    description: str = "Customer support ticket system"
    author: str = "DjangoCFG Team"
    min_djangocfg_version: str = "1.5.0"
    django_app_label: str = "support"
    url_prefix: str = "support"
    url_namespace: str = "support"

    # === Notifications ===
    telegram_enabled: bool = Field(
        default=True,
        description="Send Telegram notifications for new tickets"
    )
    email_enabled: bool = Field(
        default=True,
        description="Send Email notifications for new tickets"
    )

    # === Email settings ===
    email_template: str = Field(
        default="emails/support_notification",
        description="Email template for ticket notifications"
    )
    email_subject_new_ticket: str = Field(
        default="New Support Ticket: {subject}",
        description="Email subject for new ticket"
    )
    email_subject_new_message: str = Field(
        default="New Message in Ticket: {subject}",
        description="Email subject for new message"
    )

    # === Telegram settings ===
    telegram_new_ticket_title: str = Field(
        default="New Support Ticket",
        description="Telegram message title for new ticket"
    )
    telegram_new_message_title: str = Field(
        default="New Message in Ticket",
        description="Telegram message title for new message"
    )

    # === Admin Navigation ===
    navigation: NavigationSection = Field(
        default_factory=lambda: NavigationSection(
            title="Support",
            icon=Icons.SUPPORT_AGENT,
            collapsible=True,
            items=[
                NavigationItem(
                    title="All Tickets",
                    icon=Icons.SUPPORT_AGENT,
                    app="support",
                    model="ticket",
                ),
                NavigationItem(
                    title="Messages",
                    icon=Icons.CHAT,
                    app="support",
                    model="message",
                ),
            ],
        ),
    )
