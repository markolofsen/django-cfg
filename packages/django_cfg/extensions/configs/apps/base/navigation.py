"""
Navigation configuration models for extension apps.

Extends unfold navigation with auto-generated admin URLs for extensions.
"""

from typing import Optional, Union, Callable

from pydantic import Field, computed_field

from django_cfg.modules.django_unfold.models.navigation import (
    NavigationItem as UnfoldNavigationItem,
    NavigationSection as UnfoldNavigationSection,
)

from .constants import APP_LABEL_PREFIX


class NavigationItem(UnfoldNavigationItem):
    """
    Navigation item with automatic admin URL generation for extensions.

    Usage:
        NavigationItem(
            title="Payments",
            icon=Icons.PAYMENT,
            app="payments",      # Extension name
            model="payment",     # Model name
        )
        # Generates: /admin/cfg_payments/payment/
    """

    # Extension shortcut: app + model -> auto-generates admin URL
    app: Optional[str] = Field(None, description="Extension app name (e.g., 'payments')")
    model: Optional[str] = Field(None, description="Model name (e.g., 'payment')")

    @computed_field
    @property
    def resolved_link(self) -> Union[str, Callable]:
        """Get the link resolved for Unfold."""
        # Priority: explicit link > app+model auto-generation
        if self.link:
            from django_cfg.modules.django_unfold.utils import auto_resolve_url
            return auto_resolve_url(self.link)
        if self.app and self.model:
            return f"/admin/{APP_LABEL_PREFIX}{self.app}/{self.model}/"
        return "#"

    def get_link_for_unfold(self):
        """Get the link in the format expected by Unfold."""
        return self.resolved_link


class NavigationSection(UnfoldNavigationSection):
    """Admin navigation section configuration with icon support."""

    icon: Optional[str] = Field(None, description="Material icon name")