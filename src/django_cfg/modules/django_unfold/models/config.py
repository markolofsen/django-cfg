"""
Unfold Configuration Models

Complete configuration models for Django Unfold admin interface.
"""

from typing import List, Optional, Dict, Any, Callable
from pydantic import BaseModel, Field, ConfigDict, field_validator
from ...base import BaseCfgModule
from .navigation import NavigationSection
from .dropdown import SiteDropdownItem
from .tabs import TabConfiguration
from ..icons import Icons
import logging

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
    dashboard_callback: Optional[str] = Field(None, description="Dashboard callback function")
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
        
        # Add default navigation from dashboard manager
        try:
            from ..dashboard import DashboardManager
            dashboard = DashboardManager()
            default_nav_items = dashboard.get_navigation_config()
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

        # Dashboard callback
        if self.dashboard_callback:
            settings["DASHBOARD_CALLBACK"] = self.dashboard_callback

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
        default="ConfigToolkit Admin",
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
    
    dashboard_callback: Optional[str] = Field(
        default="django_cfg.routing.callbacks.dashboard_callback",
        description="Dashboard callback function path"
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
    
    # Tab configurations
    tab_configurations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Tab configurations for admin"
    )
    
    @field_validator('theme')
    @classmethod
    def validate_theme(cls, v: Optional[str]) -> Optional[str]:
        """Validate theme setting."""
        if v and v not in ['light', 'dark', 'auto']:
            raise ValueError("Theme must be 'light', 'dark', 'auto', or None")
        return v
    
    def get_color_scheme(self) -> Dict[str, Any]:
        """Get Unfold semantic color scheme configuration with theme support."""
        return {
            # Base semantic colors that auto-adapt to theme
            "base": {
                "50": "248, 250, 252",   # Light theme: very light background
                "100": "241, 245, 249",  # Light theme: light background  
                "200": "226, 232, 240",  # Light theme: subtle border
                "300": "203, 213, 225",  # Light theme: border
                "400": "148, 163, 184",  # Light theme: muted text / Dark theme: text
                "500": "100, 116, 139",  # Neutral - works in both themes
                "600": "71, 85, 105",    # Dark theme: muted text / Light theme: text  
                "700": "51, 65, 85",     # Dark theme: border
                "800": "30, 41, 59",     # Dark theme: subtle border
                "900": "15, 23, 42",     # Dark theme: light background
                "950": "2, 6, 23",       # Dark theme: very light background
            },
            # Primary brand - auto-adapts via CSS variables
            "primary": {
                "50": "239, 246, 255",
                "100": "219, 234, 254", 
                "200": "191, 219, 254",
                "300": "147, 197, 253",
                "400": "96, 165, 250",
                "500": "59, 130, 246",   # Main brand color
                "600": "37, 99, 235",
                "700": "29, 78, 216",
                "800": "30, 64, 175",
                "900": "30, 58, 138",
                "950": "23, 37, 84",
            },
            # Success semantic color
            "success": {
                "50": "236, 253, 245",
                "100": "209, 250, 229",
                "200": "167, 243, 208", 
                "300": "110, 231, 183",
                "400": "52, 211, 153",
                "500": "16, 185, 129",   # Main success color
                "600": "5, 150, 105",
                "700": "4, 120, 87",
                "800": "6, 95, 70",
                "900": "6, 78, 59",
                "950": "2, 44, 34",
            },
            # Warning semantic color  
            "warning": {
                "50": "255, 251, 235",
                "100": "254, 243, 199",
                "200": "253, 230, 138",
                "300": "252, 211, 77", 
                "400": "251, 191, 36",
                "500": "245, 158, 11",   # Main warning color
                "600": "217, 119, 6",
                "700": "180, 83, 9",
                "800": "146, 64, 14",
                "900": "120, 53, 15",
                "950": "69, 26, 3",
            },
            # Danger semantic color
            "danger": {
                "50": "254, 242, 242",
                "100": "254, 226, 226",
                "200": "254, 202, 202",
                "300": "252, 165, 165",
                "400": "248, 113, 113", 
                "500": "239, 68, 68",    # Main danger color
                "600": "220, 38, 38",
                "700": "185, 28, 28",
                "800": "153, 27, 27",
                "900": "127, 29, 29",
                "950": "69, 10, 10",
            },
            # Info semantic color
            "info": {
                "50": "236, 254, 255",
                "100": "207, 250, 254",
                "200": "165, 243, 252",
                "300": "103, 232, 249",
                "400": "34, 211, 238",
                "500": "6, 182, 212",    # Main info color
                "600": "8, 145, 178", 
                "700": "14, 116, 144",
                "800": "21, 94, 117",
                "900": "22, 78, 99",
                "950": "8, 51, 68",
            },
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
        if self.dashboard_callback:
            unfold_settings["DASHBOARD_CALLBACK"] = self.dashboard_callback
        
        if self.environment_callback:
            unfold_settings["ENVIRONMENT"] = self.environment_callback
        
        # Sidebar configuration
        sidebar_config = {
            "show_search": self.show_search,
            "command_search": self.command_search,
            "show_all_applications": self.show_all_applications,
        }
        
        # Get default navigation from dashboard manager
        try:
            from ..dashboard import DashboardManager
            dashboard = DashboardManager()
            nav_items = dashboard.get_navigation_config()
        except ImportError:
            nav_items = []
        
        # Add custom navigation from project (if defined)
        if self.navigation:
            # Project has custom navigation - add it first
            nav_items.extend([group.to_dict() for group in self.navigation])
        
        # Add legacy navigation_items if configured
        if self.navigation_items:
            nav_items.extend(self.navigation_items)
        
        sidebar_config["navigation"] = nav_items
        unfold_settings["SIDEBAR"] = sidebar_config
        
        # Add site dropdown - combine default from dashboard + project dropdown
        dropdown_items = []
        
        # First add default dropdown from dashboard manager
        try:
            from ..dashboard import DashboardManager
            dashboard = DashboardManager()
            dropdown_items.extend(dashboard._get_default_dropdown_items())
        except ImportError:
            pass
        
        # Then add project-specific dropdown items
        if self.site_dropdown:
            dropdown_items.extend([item.to_dict() for item in self.site_dropdown])
        elif self.site_dropdown_items:
            dropdown_items.extend(self.site_dropdown_items)
        
        if dropdown_items:
            unfold_settings["SITE_DROPDOWN"] = dropdown_items
        
        # Add tabs if configured
        if self.tab_configurations:
            unfold_settings["TABS"] = self.tab_configurations
        
        # Command interface - Enhanced for better UX
        unfold_settings["COMMAND"] = {
            "search_models": True,
            "show_history": True,
            "search_callback": None,  # Can be customized per project
        }

        # Inject universal CSS variables and custom styles
        if "STYLES" not in unfold_settings:
            unfold_settings["STYLES"] = []
        
        # Add our CSS as inline data URI
        try:
            from ..tailwind import get_css_variables, get_modal_fix_css
            import base64
            
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
    dashboard_callback: Optional[str] = Field(None, description="Dashboard callback path")
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
    
    # Tab configurations
    tab_configurations: List[TabConfiguration] = Field(
        default_factory=list,
        description="Tab configurations"
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
        if self.dashboard_callback:
            base_config["DASHBOARD_CALLBACK"] = self.dashboard_callback
        
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
        
        # Convert tabs
        if self.tab_configurations:
            tabs = []
            for tab in self.tab_configurations:
                tab_items = []
                for item in tab.items:
                    tab_item = {
                        "title": item.title,
                        "link": item.get_link_for_unfold() if hasattr(item, 'get_link_for_unfold') else item.link,
                    }
                    if item.permission:
                        tab_item["permission"] = item.permission
                    tab_items.append(tab_item)
                
                tabs.append({
                    "models": tab.models,
                    "items": tab_items,
                })
            base_config["TABS"] = tabs
        
        return base_config
