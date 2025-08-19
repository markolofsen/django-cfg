"""
Dashboard Manager for Django CFG Unfold

Manages dashboard configuration, widgets, and navigation
based on the working configuration from the old version.
"""

from typing import List, Dict, Any, Optional
from django.templatetags.static import static
from django.urls import reverse_lazy
from ..base import BaseModule


class DashboardManager(BaseModule):
    """
    Dashboard configuration manager for Unfold.
    
    Based on the working configuration from @old/api__old/api/dashboard/unfold_config.py
    """
    
    def __init__(self):
        """Initialize dashboard manager."""
        super().__init__()
        self.config = self.get_config()
    
    def get_navigation_config(self) -> List[Dict[str, Any]]:
        """Get navigation configuration for Unfold sidebar."""
        return [
            {
                "title": "Dashboard",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Overview",
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                    {
                        "title": "Analytics",
                        "icon": "analytics",
                        "link": reverse_lazy("admin:index"),
                    },
                    {
                        "title": "Reports",
                        "icon": "assessment",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": "Data Management",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Users",
                        "icon": "people",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                    },
                    {
                        "title": "Groups",
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
            {
                "title": "System",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Settings",
                        "icon": "settings",
                        "link": reverse_lazy("admin:index"),
                    },
                    {
                        "title": "Logs",
                        "icon": "list_alt",
                        "link": reverse_lazy("admin:index"),
                    },
                    {
                        "title": "Backups",
                        "icon": "backup",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
        ]
    
    def get_unfold_config(self) -> Dict[str, Any]:
        """Get complete Unfold configuration based on working old version."""
        return {
            # Site branding and appearance
            "SITE_TITLE": "CarAPIS Admin",
            "SITE_HEADER": "CarAPIS",
            "SITE_SUBHEADER": "Automotive Data Platform",
            "SITE_URL": "/",
            "SITE_SYMBOL": "directions_car",
            
            # UI visibility controls
            "SHOW_HISTORY": True,
            "SHOW_VIEW_ON_SITE": True,
            "SHOW_BACK_BUTTON": False,
            
            # Dashboard callback
            "DASHBOARD_CALLBACK": "api.dashboard.callbacks.main_dashboard_callback",
            
            # Theme configuration
            "THEME": None,  # Auto-detect or force "dark"/"light"
            
            # Login page customization
            "LOGIN": {
                "redirect_after": lambda request: reverse_lazy("admin:index"),
            },
            
            # Design system
            "BORDER_RADIUS": "8px",
            "COLORS": {
                "base": {
                    "50": "249, 250, 251",
                    "100": "243, 244, 246",
                    "200": "229, 231, 235",
                    "300": "209, 213, 219",
                    "400": "156, 163, 175",
                    "500": "107, 114, 128",
                    "600": "75, 85, 99",
                    "700": "55, 65, 81",
                    "800": "31, 41, 55",
                    "900": "17, 24, 39",
                    "950": "3, 7, 18",
                },
                "primary": {
                    "50": "239, 246, 255",
                    "100": "219, 234, 254",
                    "200": "191, 219, 254",
                    "300": "147, 197, 253",
                    "400": "96, 165, 250",
                    "500": "59, 130, 246",
                    "600": "37, 99, 235",
                    "700": "29, 78, 216",
                    "800": "30, 64, 175",
                    "900": "30, 58, 138",
                    "950": "23, 37, 84",
                },
                "font": {
                    "subtle-light": "var(--color-base-500)",
                    "subtle-dark": "var(--color-base-400)",
                    "default-light": "var(--color-base-600)",
                    "default-dark": "var(--color-base-300)",
                    "important-light": "var(--color-base-900)",
                    "important-dark": "var(--color-base-100)",
                },
            },
            
            # Sidebar navigation - КЛЮЧЕВАЯ СТРУКТУРА!
            "SIDEBAR": {
                "show_search": True,
                "command_search": True,
                "show_all_applications": True,
                "navigation": self.get_navigation_config(),
            },
            
            # Site dropdown menu
            "SITE_DROPDOWN": [
                {
                    "icon": "language",
                    "title": "Documentation",
                    "link": "https://docs.carapis.com",
                },
                {
                    "icon": "support_agent",
                    "title": "Support",
                    "link": "https://support.carapis.com",
                },
                {
                    "icon": "code",
                    "title": "API Docs",
                    "link": "https://api.carapis.com/docs",
                },
                {
                    "icon": "bug_report",
                    "title": "Report Issue",
                    "link": "https://github.com/carapis/issues",
                },
            ],
            
            # Command interface
            "COMMAND": {
                "search_models": True,
                "show_history": True,
            },
            
            # Multi-language support - DISABLED
            "SHOW_LANGUAGES": False,
        }
    
    def get_widgets_config(self) -> List[Dict[str, Any]]:
        """Get dashboard widgets configuration."""
        return [
            {
                "type": "stats_cards",
                "title": "System Overview",
                "cards": [
                    {
                        "title": "CPU Usage",
                        "value_template": "{{ cpu_percent }}%",
                        "icon": "memory",
                        "color": "blue",
                    },
                    {
                        "title": "Memory Usage", 
                        "value_template": "{{ memory_percent }}%",
                        "icon": "storage",
                        "color": "green",
                    },
                    {
                        "title": "Disk Usage",
                        "value_template": "{{ disk_percent }}%",
                        "icon": "folder",
                        "color": "orange",
                    },
                ]
            },
        ]


# Create global instance for easy import
dashboard_manager = DashboardManager()
