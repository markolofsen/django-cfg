"""
Unfold Configuration Models for django_cfg.

Provides type-safe configuration for Django Unfold admin interface.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from django_cfg.tailwind.config import get_unfold_colors
from django.urls import reverse_lazy, NoReverseMatch


class UnfoldColors(BaseModel):
    """Unfold color theme configuration."""

    primary: Optional[str] = Field(None, description="Primary color")
    success: Optional[str] = Field(None, description="Success color")
    warning: Optional[str] = Field(None, description="Warning color")
    danger: Optional[str] = Field(None, description="Danger color")
    info: Optional[str] = Field(None, description="Info color")


class UnfoldSidebar(BaseModel):
    """Unfold sidebar configuration."""

    show_search: bool = Field(True, description="Show search in sidebar")
    show_all_applications: bool = Field(True, description="Show all applications")
    navigation: List[Dict[str, Any]] = Field(default_factory=list, description="Custom navigation")


class NavigationItem(BaseModel):
    """Single navigation item configuration."""

    title: str = Field(..., description="Navigation item title")
    icon: Optional[str] = Field(None, description="Material icon name")
    link: Optional[str] = Field(None, description="Navigation link")
    badge: Optional[str] = Field(None, description="Badge text")
    separator: bool = Field(False, description="Is separator item")


class NavigationGroup(BaseModel):
    """Navigation group configuration."""

    title: str = Field(..., description="Group title")
    separator: bool = Field(False, description="Add separator before group")
    collapsible: bool = Field(True, description="Group is collapsible")
    items: List[NavigationItem] = Field(default_factory=list, description="Group items")


class DropdownItem(BaseModel):
    """Dropdown menu item configuration."""

    title: str = Field(..., description="Item title")
    icon: str = Field(..., description="Material icon name")
    link: str = Field(..., description="Item URL")


class QuickAction(BaseModel):
    """Quick action configuration for dashboard."""

    title: str = Field(..., description="Action title")
    icon: str = Field(..., description="Material icon name")
    url: str = Field(..., description="Action URL")
    description: Optional[str] = Field(None, description="Action description")
    color: Optional[str] = Field(None, description="Action color")


def get_reverse_lazy(link: str) -> str:
    try:
        return reverse_lazy(link)
    except NoReverseMatch:
        return link


class DashboardWidget(BaseModel):
    """Dashboard widget configuration."""

    title: str = Field(..., description="Widget title")
    template: Optional[str] = Field(None, description="Custom template path")
    callback: Optional[str] = Field(None, description="Callback function path")
    width: int = Field(12, description="Widget width (1-12)")
    order: int = Field(0, description="Widget order")


class UnfoldTheme(BaseModel):
    """Complete Unfold theme configuration."""

    # Basic theme settings
    site_title: str = Field("Django Admin", description="Site title")
    site_header: str = Field("Django Administration", description="Site header")
    site_url: str = Field("/", description="Site URL")
    site_symbol: str = Field("speed", description="Material icon for site")

    # UI settings
    show_history: bool = Field(True, description="Show history in admin")
    show_view_on_site: bool = Field(True, description="Show view on site links")
    show_back_button: bool = Field(False, description="Show back button")

    # Theme and appearance
    theme: Optional[str] = Field(None, description="Theme: light, dark, or None for switcher")
    colors: UnfoldColors = Field(default_factory=UnfoldColors, description="Color theme")
    sidebar: UnfoldSidebar = Field(default_factory=UnfoldSidebar, description="Sidebar config")

    # Dashboard
    dashboard_callback: Optional[str] = Field(None, description="Dashboard callback function")
    environment_callback: Optional[str] = Field(None, description="Environment callback function")

    # Navigation
    navigation: List[NavigationGroup] = Field(default_factory=list, description="Custom navigation")

    # Site dropdown menu
    site_dropdown: List[DropdownItem] = Field(default_factory=list, description="Site dropdown menu items")

    # Quick actions and widgets
    quick_actions: List[QuickAction] = Field(default_factory=list, description="Dashboard quick actions")
    widgets: List[DashboardWidget] = Field(default_factory=list, description="Dashboard widgets")

    def to_django_settings(self) -> Dict[str, Any]:
        """Convert to Django UNFOLD settings."""
        # Try to import colors, fallback to base colors if not available
        colors = get_unfold_colors()

        settings = {
            "SITE_TITLE": self.site_title,
            "SITE_HEADER": self.site_header,
            "SITE_URL": self.site_url,
            "SITE_SYMBOL": self.site_symbol,
            "SHOW_HISTORY": self.show_history,
            "SHOW_VIEW_ON_SITE": self.show_view_on_site,
            "SHOW_BACK_BUTTON": self.show_back_button,
            "COLORS": colors,
            "BORDER_RADIUS": "8px",
        }

        # Theme settings
        if self.theme:
            settings["THEME"] = self.theme

        # Sidebar configuration - KEY PART!
        sidebar_config = {
            "show_search": self.sidebar.show_search,
            "command_search": True,
            "show_all_applications": self.sidebar.show_all_applications,
        }

        # Add navigation to sidebar - take from navigation field, not from sidebar.navigation
        if self.navigation:
            # Convert NavigationGroup models to dictionaries with reverse_lazy
            nav_items = []
            for group in self.navigation:
                group_dict = {
                    "title": group.title,
                    "separator": group.separator,
                    "collapsible": group.collapsible,
                    "items": [
                        {
                            "title": item.title,
                            "icon": item.icon,
                            "link": get_reverse_lazy(item.link),
                        }
                        for item in group.items
                    ],
                }
                nav_items.append(group_dict)
            sidebar_config["navigation"] = nav_items

        settings["SIDEBAR"] = sidebar_config

        # Command interface
        settings["COMMAND"] = {
            "search_models": True,
            "show_history": True,
        }

        # Multi-language support - DISABLED
        settings["SHOW_LANGUAGES"] = False

        # Site dropdown menu
        if self.site_dropdown:
            settings["SITE_DROPDOWN"] = [
                {
                    "icon": item.icon,
                    "title": item.title,
                    "link": item.link,
                }
                for item in self.site_dropdown
            ]

        # Dashboard callback
        if self.dashboard_callback:
            settings["DASHBOARD_CALLBACK"] = self.dashboard_callback

        # Environment callback
        if self.environment_callback:
            settings["ENVIRONMENT_CALLBACK"] = self.environment_callback

        return settings


class UnfoldConfig(BaseModel):
    """
    Main Unfold configuration for django_cfg.

    Usage:
        unfold = UnfoldConfig(
            theme=UnfoldTheme(
                site_title="My Admin",
                site_header="My Project Admin",
            )
        )
    """

    enabled: bool = Field(True, description="Enable Unfold admin interface")
    theme: UnfoldTheme = Field(default_factory=UnfoldTheme, description="Unfold theme configuration")

    # Additional settings that can be overridden
    additional_settings: Dict[str, Any] = Field(default_factory=dict, description="Additional Django UNFOLD settings")

    def to_django_settings(self) -> Dict[str, Any]:
        """Generate Django settings for Unfold."""
        if not self.enabled:
            return {}

        # Get base settings from theme
        unfold_settings = self.theme.to_django_settings()

        # Merge additional settings
        unfold_settings.update(self.additional_settings)

        return {"UNFOLD": unfold_settings}

    def get_installed_apps(self) -> List[str]:
        """Get required installed apps for Unfold."""
        if not self.enabled:
            return []

        return [
            "unfold",  # Must be before django.contrib.admin
            "unfold.contrib.filters",  # Optional filters
            "unfold.contrib.forms",  # Optional form elements
            "unfold.contrib.inlines",  # Inline forms
            "unfold.contrib.import_export",  # Import/export functionality
            "unfold.contrib.guardian",  # Guardian permissions
            "unfold.contrib.simple_history",  # Simple history
            "unfold.contrib.location_field",  # Location fields
            "unfold.contrib.constance",  # Constance integration
        ]
