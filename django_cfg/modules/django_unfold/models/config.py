"""
Unfold Configuration Models

Complete configuration models for Django Unfold admin interface.
"""

import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from django_cfg.modules.django_admin.icons import Icons

from .dropdown import SiteDropdownItem
from .navigation import NavigationSection

logger = logging.getLogger(__name__)




class UnfoldColors(BaseModel):
    """Unfold color theme configuration."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    primary: Optional[str] = Field(None, description="Primary color")
    success: Optional[str] = Field(None, description="Success color")
    warning: Optional[str] = Field(None, description="Warning color")
    danger: Optional[str] = Field(None, description="Danger color")
    info: Optional[str] = Field(None, description="Info color")


class UnfoldSidebar(BaseModel):
    """Unfold sidebar configuration."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    show_search: bool = Field(True, description="Show search in sidebar")
    show_all_applications: bool = Field(True, description="Show all applications")
    navigation: List[Dict[str, Any]] = Field(default_factory=list, description="Custom navigation")


class UnfoldTheme(BaseModel):
    """Complete Unfold theme configuration."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    # Basic theme settings
    site_title: str = Field("Django Admin", description="Site title")
    site_header: str = Field("Django Administration", description="Site header")
    site_url: str = Field("/", description="Site URL")
    site_symbol: str = Field(Icons.ROCKET_LAUNCH, description="Material icon for site")

    # UI settings
    show_history: bool = Field(True, description="Show history in admin")
    show_view_on_site: bool = Field(True, description="Show view on site links")
    show_back_button: bool = Field(False, description="Show back button")

    # Theme and appearance
    theme: Optional[str] = Field(None, description="Theme: light, dark, or None for switcher")
    colors: UnfoldColors = Field(default_factory=UnfoldColors, description="Color theme")
    sidebar: UnfoldSidebar = Field(default_factory=UnfoldSidebar, description="Sidebar config")

    # Dashboard
    environment_callback: Optional[str] = Field(None, description="Environment callback function")

    # Navigation
    navigation: List[NavigationSection] = Field(default_factory=list, description="Custom navigation")

    # Site dropdown menu
    site_dropdown: List[SiteDropdownItem] = Field(default_factory=list, description="Site dropdown menu items")

    def to_django_settings(self) -> Dict[str, Any]:
        """Convert to Django UNFOLD settings."""
        # Try to import colors, fallback to base colors if not available
        try:
            from ..tailwind import get_unfold_colors
            colors = get_unfold_colors()
        except ImportError:
            colors = {
                "primary": {
                    "500": "59, 130, 246",
                },
                "base": {
                    "500": "107, 114, 128",
                }
            }

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

        # Start with custom navigation from project (if defined)
        nav_items = []
        if self.navigation:
            # Project has custom navigation - add it first
            nav_items.extend([group.to_dict() for group in self.navigation])

        # Add default navigation from navigation manager
        try:
            from ..navigation import NavigationManager
            nav_manager = NavigationManager()
            default_nav_items = nav_manager.get_navigation_config()
            nav_items.extend(default_nav_items)
        except ImportError:
            pass

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
            settings["SITE_DROPDOWN"] = [item.to_dict() for item in self.site_dropdown]

        # Environment callback
        if self.environment_callback:
            settings["ENVIRONMENT_CALLBACK"] = self.environment_callback

        return settings


class UnfoldThemeConfig(UnfoldTheme):
    """Unfold theme configuration."""
    pass


class UnfoldConfig(BaseModel):
    """
    🎨 Unfold Configuration - Django Unfold admin interface
    
    Complete configuration for Django Unfold admin with dashboard,
    navigation, theming, and callback support.
    """
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    # Site branding
    site_title: str = Field(
        default="Django-CFG Admin",
        description="Site title shown in admin"
    )

    site_header: str = Field(
        default="Django Config Toolkit",
        description="Site header text"
    )

    site_subheader: str = Field(
        default="🚀 Type-safe Django Configuration",
        description="Site subheader text"
    )

    site_symbol: str = Field(
        default="settings",
        description="Material icon symbol for site"
    )

    site_url: str = Field(
        default="/",
        description="Site URL"
    )

    # UI settings
    show_history: bool = Field(
        default=True,
        description="Show history in admin"
    )

    show_view_on_site: bool = Field(
        default=True,
        description="Show 'View on site' links"
    )

    show_back_button: bool = Field(
        default=False,
        description="Show back button in admin"
    )

    # Theme settings
    theme: Optional[str] = Field(
        default=None,
        description="Theme setting (light/dark/auto)"
    )

    border_radius: str = Field(
        default="8px",
        description="Border radius for UI elements"
    )

    # Dashboard settings
    dashboard_enabled: bool = Field(
        default=True,
        description="Enable custom dashboard"
    )

    environment_callback: Optional[str] = Field(
        default="django_cfg.routing.callbacks.environment_callback",
        description="Environment callback function path"
    )

    # Navigation settings
    show_search: bool = Field(
        default=True,
        description="Show search in sidebar"
    )

    command_search: bool = Field(
        default=True,
        description="Enable command search"
    )

    show_all_applications: bool = Field(
        default=True,
        description="Show all applications in sidebar"
    )

    # Multi-language settings
    show_languages: bool = Field(
        default=False,
        description="Show language switcher"
    )

    # Colors configuration
    colors: Optional[UnfoldColors] = Field(
        default=None,
        description="Color theme configuration"
    )

    # Sidebar configuration
    sidebar: Optional[UnfoldSidebar] = Field(
        default=None,
        description="Sidebar configuration"
    )

    # Navigation items
    navigation: List[NavigationSection] = Field(
        default_factory=list,
        description="Custom navigation sections"
    )

    navigation_items: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Custom navigation items (legacy)"
    )

    # Site dropdown items
    site_dropdown: List[SiteDropdownItem] = Field(
        default_factory=list,
        description="Site dropdown menu items"
    )

    site_dropdown_items: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Site dropdown menu items (legacy)"
    )

    # Login configuration
    login_form: Optional[str] = Field(
        default=None,
        description="Custom login form class path"
    )

    # Development autofill
    dev_autofill_email: Optional[str] = Field(
        default=None,
        description="Email for autofill"
    )

    dev_autofill_password: Optional[str] = Field(
        default=None,
        description="Password for autofill"
    )

    dev_autofill_force: bool = Field(
        default=False,
        description="Force autofill even in production (ignores DEBUG check)"
    )

    @field_validator('theme')
    @classmethod
    def validate_theme(cls, v: Optional[str]) -> Optional[str]:
        """Validate theme setting."""
        if v and v not in ['light', 'dark', 'auto']:
            raise ValueError("Theme must be 'light', 'dark', 'auto', or None")
        return v

    def get_color_scheme(self) -> Dict[str, Any]:
        """
        Get Unfold semantic color scheme configuration matching Next.js UI package.

        Colors are synchronized with:
        - packages/ui/src/styles/theme/light.css
        - packages/ui/src/styles/theme/dark.css

        This ensures consistent theming between Django Unfold and Next.js iframe.

        IMPORTANT: Colors must be in OKLCH format for Unfold's color-mix() CSS to work!
        Format: "oklch(lightness% chroma hue)"
        """
        return {
            # Base semantic colors - matches Next.js UI package
            # Light theme: Clean whites and neutral grays (Vercel-inspired)
            # Dark theme: True black backgrounds with subtle grays
            # Converted from RGB to OKLCH for color-mix() compatibility
            "base": {
                "50": "oklch(98.5% .002 247.839)",   # #f9fafb - Very light background
                "100": "oklch(96.7% .003 264.542)",  # #f3f4f6 - Light background (96%)
                "200": "oklch(92.8% .006 264.531)",  # #e5e7eb - Subtle border (90%)
                "300": "oklch(87.2% .010 258.338)",  # #d1d5db - Border
                "400": "oklch(70.7% .022 261.325)",  # #9ca3af - Muted text
                "500": "oklch(55.1% .027 264.364)",  # #6b7280 - Neutral
                "600": "oklch(44.6% .030 256.802)",  # #4b5563 - Text (9%)
                "700": "oklch(37.3% 0 0)",           # Neutral dark gray (no hue)
                "800": "oklch(20.0% 0 0)",           # Dark card background (no hue)
                "900": "oklch(14.0% 0 0)",           # Main background - near black (14%)
                "950": "oklch(10.0% 0 0)",           # Deepest black (10%)
            },
            # Primary brand color - Blue (#3b82f6 / hsl(217 91% 60%))
            # Matches Next.js UI primary color
            # OKLCH format for color-mix() compatibility
            "primary": {
                "50": "oklch(97.0% .014 254.604)",   # #eff6ff
                "100": "oklch(93.2% .032 255.585)",  # #dbeafe
                "200": "oklch(88.2% .059 254.128)",  # #bfdbfe
                "300": "oklch(79.0% .099 253.800)",  # #93c5fd
                "400": "oklch(70.7% .165 254.624)",  # #60a5fa
                "500": "oklch(62.3% .214 259.815)",  # #3b82f6 - Main brand color
                "600": "oklch(54.6% .245 262.881)",  # #2563eb
                "700": "oklch(48.8% .243 264.376)",  # #1d4ed8
                "800": "oklch(43.0% .223 265.500)",  # #1e40af
                "900": "oklch(37.5% .195 266.000)",  # #1e3a8a
                "950": "oklch(30.0% .150 267.000)",  # #172554
            },
            # Success color - Green
            # OKLCH format for color-mix() compatibility
            "success": {
                "50": "oklch(98.0% .029 156.743)",   # #f0fdf4
                "100": "oklch(96.2% .044 156.743)",  # #dcfce7
                "200": "oklch(92.5% .084 155.995)",  # #bbf7d0
                "300": "oklch(87.0% .139 154.500)",  # #86efac
                "400": "oklch(79.2% .209 151.711)",  # #4ade80
                "500": "oklch(72.3% .219 149.579)",  # #22c55e - Main success
                "600": "oklch(62.7% .194 149.214)",  # #16a34a
                "700": "oklch(52.7% .154 150.069)",  # #15803d
                "800": "oklch(45.0% .125 151.000)",  # #166534
                "900": "oklch(38.0% .100 151.500)",  # #14532d
                "950": "oklch(25.0% .060 152.000)",  # #052e16
            },
            # Warning color - Amber/Yellow
            # OKLCH format for color-mix() compatibility
            "warning": {
                "50": "oklch(99.0% .020 95.617)",    # #fffbeb
                "100": "oklch(96.2% .059 95.617)",   # #fef3c7
                "200": "oklch(94.5% .129 101.54)",   # #fde68a
                "300": "oklch(89.0% .178 100.000)",  # #fcd34d
                "400": "oklch(83.0% .198 95.000)",   # #fbbf24
                "500": "oklch(70.5% .213 47.604)",   # #f59e0b - Main warning
                "600": "oklch(64.6% .222 41.116)",   # #d97706
                "700": "oklch(55.3% .195 38.402)",   # #b45309
                "800": "oklch(48.0% .170 37.000)",   # #92400e
                "900": "oklch(41.0% .145 38.000)",   # #78350f
                "950": "oklch(30.0% .100 40.000)",   # #451a03
            },
            # Danger/Error color - Red (matches destructive color)
            # OKLCH format for color-mix() compatibility
            "danger": {
                "50": "oklch(98.0% .011 17.38)",     # #fef2f2
                "100": "oklch(95.5% .027 17.717)",   # #fee2e2
                "200": "oklch(93.6% .032 17.717)",   # #fecaca
                "300": "oklch(88.5% .062 18.334)",   # #fca5a5
                "400": "oklch(80.8% .114 19.571)",   # #f87171
                "500": "oklch(63.7% .237 25.331)",   # #ef4444 - Main danger
                "600": "oklch(57.7% .245 27.325)",   # #dc2626
                "700": "oklch(50.5% .213 27.518)",   # #b91c1c
                "800": "oklch(45.0% .190 28.000)",   # #991b1b
                "900": "oklch(40.0% .165 28.500)",   # #7f1d1d
                "950": "oklch(30.0% .120 29.000)",   # #450a0a
            },
            # Info color - Cyan/Sky blue
            # OKLCH format for color-mix() compatibility
            "info": {
                "50": "oklch(97.5% .015 230.000)",   # #f0f9ff
                "100": "oklch(95.0% .035 230.000)",  # #e0f2fe
                "200": "oklch(90.0% .070 225.000)",  # #bae6fd
                "300": "oklch(82.0% .120 220.000)",  # #7dd3fc
                "400": "oklch(74.0% .155 217.000)",  # #38bdf8
                "500": "oklch(67.0% .184 215.000)",  # #0ea5e9 - Main info
                "600": "oklch(58.0% .185 218.000)",  # #0284c7
                "700": "oklch(49.0% .165 220.000)",  # #0369a1
                "800": "oklch(42.0% .140 222.000)",  # #075985
                "900": "oklch(36.0% .115 224.000)",  # #0c4a6e
                "950": "oklch(28.0% .085 226.000)",  # #082f49
            },
            # Font semantic colors (using OKLCH format)
            "font": {
                "subtle-light": "oklch(55.1% .027 264.364)",    # base-500 #6b7280
                "subtle-dark": "oklch(70.7% .022 261.325)",     # base-400 #9ca3af
                "default-light": "oklch(44.6% .030 256.802)",   # base-600 #4b5563
                "default-dark": "oklch(87.2% .010 258.338)",    # base-300 #d1d5db
                "important-light": "oklch(14.0% 0 0)",          # base-900 (near black)
                "important-dark": "oklch(96.7% .003 264.542)",  # base-100 #f3f4f6
            }
        }

    def to_django_settings(self) -> Dict[str, Any]:
        """Generate Django settings for Unfold."""
        # Base Unfold configuration
        unfold_settings = {
            "SITE_TITLE": self.site_title,
            "SITE_HEADER": self.site_header,
            "SITE_SUBHEADER": self.site_subheader,
            "SITE_URL": self.site_url,
            "SITE_SYMBOL": self.site_symbol,
            "SHOW_HISTORY": self.show_history,
            "SHOW_VIEW_ON_SITE": self.show_view_on_site,
            "SHOW_BACK_BUTTON": self.show_back_button,
            "THEME": self.theme,
            "BORDER_RADIUS": self.border_radius,
            "SHOW_LANGUAGES": self.show_languages,
            "COLORS": self.get_color_scheme(),
        }

        # Add callbacks if configured
        if self.environment_callback:
            unfold_settings["ENVIRONMENT"] = self.environment_callback

        # Sidebar configuration
        sidebar_config = {
            "show_search": self.show_search,
            "command_search": self.command_search,
            "show_all_applications": self.show_all_applications,
        }

        # Make navigation callable to defer URL resolution until Django is ready
        def get_navigation(request=None):
            """Generate navigation - called when Django is ready, not during settings init."""
            nav_items = []

            # Get default navigation from navigation manager first
            try:
                from ..navigation import NavigationManager
                nav_manager = NavigationManager()
                nav_items = nav_manager.get_navigation_config()
            except Exception:
                pass

            # Add custom navigation from project (if defined) - appears after default
            if self.navigation:
                # Now it's safe to call to_dict() - Django URLs are ready
                from django.urls import reverse
                for group in self.navigation:
                    # Convert NavigationSection to dict, resolving URL names
                    group_dict = {
                        "title": group.title,
                        "separator": group.separator,
                        "collapsible": group.collapsible,
                        "items": []
                    }
                    if group.open:
                        group_dict["open"] = True

                    # Resolve each item's URL
                    for item in group.items:
                        item_link = item.link or "#"
                        # Try to resolve URL names
                        if not item_link.startswith(("/", "http", "#")):
                            try:
                                item_link = reverse(item_link)
                            except Exception:
                                pass  # Keep original if reverse fails

                        group_dict["items"].append({
                            "title": item.title,
                            "icon": item.icon,
                            "link": item_link,
                            "badge": item.badge,
                            "permission": item.permission,
                        })

                    nav_items.append(group_dict)

            # Add legacy navigation_items if configured
            if self.navigation_items:
                nav_items.extend(self.navigation_items)

            return nav_items

        sidebar_config["navigation"] = get_navigation
        unfold_settings["SIDEBAR"] = sidebar_config

        # Add site dropdown - combine default from dashboard + project dropdown
        dropdown_items = []

        # First add default dropdown items
        try:
            from django_cfg.config import get_default_dropdown_items
            dropdown_items.extend([item.to_dict() for item in get_default_dropdown_items()])
        except (ImportError, Exception):
            pass

        # Then add project-specific dropdown items
        if self.site_dropdown:
            dropdown_items.extend([item.to_dict() for item in self.site_dropdown])
        elif self.site_dropdown_items:
            dropdown_items.extend(self.site_dropdown_items)

        if dropdown_items:
            unfold_settings["SITE_DROPDOWN"] = dropdown_items

        # Command interface - Enhanced for better UX
        unfold_settings["COMMAND"] = {
            "search_models": True,
            "show_history": True,
            "search_callback": None,  # Can be customized per project
        }

        # Development autofill
        if self.dev_autofill_email:
            unfold_settings["DEV_AUTOFILL_EMAIL"] = self.dev_autofill_email
        if self.dev_autofill_password:
            unfold_settings["DEV_AUTOFILL_PASSWORD"] = self.dev_autofill_password
        if self.dev_autofill_force:
            unfold_settings["DEV_AUTOFILL_FORCE"] = self.dev_autofill_force

        # Login configuration - auto-enable DevAuthForm if autofill is set
        login_form = self.login_form
        if not login_form and (self.dev_autofill_email or self.dev_autofill_password):
            login_form = "django_cfg.modules.django_unfold.forms.DevAuthForm"

        if login_form:
            unfold_settings["LOGIN"] = {"form": login_form}

        # Inject universal CSS variables and custom styles
        if "STYLES" not in unfold_settings:
            unfold_settings["STYLES"] = []

        # Add our CSS as inline data URI
        try:
            import base64

            from ..tailwind import get_css_variables, get_modal_fix_css

            # Base CSS variables
            css_content = get_css_variables()

            # Add modal scroll fix CSS
            css_content += get_modal_fix_css()

            css_b64 = base64.b64encode(css_content.encode('utf-8')).decode('utf-8')
            data_uri = f"data:text/css;base64,{css_b64}"
            unfold_settings["STYLES"].append(lambda request: data_uri)
        except ImportError:
            pass

        return {"UNFOLD": unfold_settings}


class UnfoldDashboardConfig(BaseModel):
    """Complete Unfold dashboard configuration."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    # Site branding
    site_title: str = Field(default="Admin Dashboard", description="Site title")
    site_header: str = Field(default="Admin", description="Site header")
    site_subheader: str = Field(default="Management Interface", description="Site subheader")
    site_url: str = Field(default="/", description="Site URL")
    site_symbol: str = Field(default=Icons.ADMIN_PANEL_SETTINGS, description="Site icon")

    # UI settings
    show_history: bool = Field(default=True, description="Show history")
    show_view_on_site: bool = Field(default=True, description="Show view on site")
    show_back_button: bool = Field(default=False, description="Show back button")
    theme: Optional[str] = Field(default=None, description="Theme (light/dark) or None for theme switcher")
    show_languages: bool = Field(default=False, description="Show language switcher")
    show_theme_switcher: bool = Field(default=True, description="Show theme switcher (requires theme=None)")

    # Callbacks
    environment_callback: Optional[str] = Field(None, description="Environment callback path")

    # Navigation configuration
    navigation_sections: List[NavigationSection] = Field(
        default_factory=list,
        description="Navigation sections"
    )

    # Site dropdown configuration
    site_dropdown_items: List[SiteDropdownItem] = Field(
        default_factory=list,
        description="Site dropdown items"
    )

    def to_unfold_dict(self) -> Dict[str, Any]:
        """Convert to Unfold configuration dictionary."""
        base_config = {
            "SITE_TITLE": self.site_title,
            "SITE_HEADER": self.site_header,
            "SITE_SUBHEADER": self.site_subheader,
            "SITE_URL": self.site_url,
            "SITE_SYMBOL": self.site_symbol,
            "SHOW_HISTORY": self.show_history,
            "SHOW_VIEW_ON_SITE": self.show_view_on_site,
            "SHOW_BACK_BUTTON": self.show_back_button,
            "SHOW_LANGUAGES": self.show_languages,
        }

        # Theme configuration: None enables theme switcher, string value forces theme
        if self.show_theme_switcher and self.theme is None:
            # Don't set THEME key - this enables theme switcher
            pass
        else:
            # Set specific theme - this disables theme switcher
            base_config["THEME"] = self.theme

        # Add callbacks if configured
        if self.environment_callback:
            base_config["ENVIRONMENT"] = self.environment_callback

        # Sidebar configuration
        sidebar_config = {
            "show_search": True,
            "command_search": True,
            "show_all_applications": True,
        }

        # Convert navigation sections
        if self.navigation_sections:
            sidebar_config["navigation"] = [section.to_dict() for section in self.navigation_sections]

        base_config["SIDEBAR"] = sidebar_config

        # Convert site dropdown
        if self.site_dropdown_items:
            base_config["SITE_DROPDOWN"] = [item.to_dict() for item in self.site_dropdown_items]

        return base_config
