"""
Navigation configuration models for extension apps.

Extends the admin site navigation models with auto-generated admin URLs for extensions.
"""

from typing import Optional, Union, Callable

from pydantic import Field, computed_field

from django_cfg.modules.admin_site.models.navigation import (
    NavigationItem as SiteNavigationItem,
    NavigationSection as SiteNavigationSection,
)

from .constants import APP_LABEL_PREFIX


class NavigationItem(SiteNavigationItem):
    """
    Navigation item with automatic admin URL generation for extensions.

    Usage:
        NavigationItem(
            title="Payments",
            icon=Icons.PAYMENT,
            app="payments",      # Extension name
            model="payment",     # Model name
        )
        # Generates: <admin prefix>cfg_payments/payment/
    """

    # Extension shortcut: app + model -> auto-generates admin URL
    app: Optional[str] = Field(None, description="Extension app name (e.g., 'payments')")
    model: Optional[str] = Field(None, description="Model name (e.g., 'payment')")

    @computed_field
    @property
    def resolved_link(self) -> Union[str, Callable]:
        """The link: explicit link, else the app+model admin URL."""
        # Priority: explicit link > app+model auto-generation
        if self.link:
            from django_cfg.modules.admin_site.utils import auto_resolve_url
            return auto_resolve_url(self.link)
        if self.app and self.model:
            from django_cfg.core.admin_access import get_admin_prefix

            return f"{get_admin_prefix()}{APP_LABEL_PREFIX}{self.app}/{self.model}/"
        return "#"


class NavigationSection(SiteNavigationSection):
    """Admin navigation section configuration with icon support."""

    icon: Optional[str] = Field(None, description="Material icon name")