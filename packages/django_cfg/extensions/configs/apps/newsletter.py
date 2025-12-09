"""
Base configuration for newsletter extension.

Users extend this class in their extension's __cfg__.py:

    from django_cfg.extensions.configs.apps.newsletter import BaseNewsletterSettings

    class NewsletterSettings(BaseNewsletterSettings):
        pass

    settings = NewsletterSettings()
"""

from pydantic import Field

from django_cfg.modules.django_admin.icons import Icons

from .base import BaseExtensionSettings, NavigationItem, NavigationSection


class BaseNewsletterSettings(BaseExtensionSettings):
    """Base settings for newsletter extension."""

    # === Manifest defaults ===
    name: str = "newsletter"
    version: str = "1.0.0"
    description: str = "Newsletter and email campaigns"
    author: str = "DjangoCFG Team"
    min_djangocfg_version: str = "1.5.0"
    django_app_label: str = "newsletter"
    url_prefix: str = "newsletter"
    url_namespace: str = "newsletter"

    # === Admin Navigation ===
    navigation: NavigationSection = Field(
        default_factory=lambda: NavigationSection(
            title="Newsletter",
            icon=Icons.EMAIL,
            collapsible=True,
            items=[
                NavigationItem(
                    title="Newsletters",
                    icon=Icons.EMAIL,
                    app="newsletter",
                    model="newsletter",
                ),
                NavigationItem(
                    title="Subscriptions",
                    icon=Icons.PERSON_ADD,
                    app="newsletter",
                    model="newslettersubscription",
                ),
                NavigationItem(
                    title="Campaigns",
                    icon=Icons.CAMPAIGN,
                    app="newsletter",
                    model="newslettercampaign",
                ),
                NavigationItem(
                    title="Email Logs",
                    icon=Icons.MAIL_OUTLINE,
                    app="newsletter",
                    model="emaillog",
                ),
            ],
        ),
    )
