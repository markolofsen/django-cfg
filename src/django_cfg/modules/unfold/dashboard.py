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
        """Get complete default navigation configuration for Unfold sidebar."""
        navigation = [
            {
                "title": "Dashboard",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Overview",
                        "icon": "dashboard",
                        "link": "/admin/",
                    },
                    {
                        "title": "Settings",
                        "icon": "settings",
                        "link": '/admin/constance/config/',
                    },
                    {
                        "title": "Health Check",
                        "icon": "health_and_safety",
                        "link": "/cfg/health/",
                    },
                ],
            },
        ]
        
        # Add Accounts section if enabled
        if self.is_accounts_enabled():
            navigation.append({
                "title": "Users & Access",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Users",
                        "icon": "people",
                        "link": "/admin/django_cfg_accounts/customuser/",
                    },

                    {
                        "title": "User Groups",
                        "icon": "group",
                        "link": "/admin/auth/group/",
                    },
                    {
                        "title": "Registration Sources",
                        "icon": "link",
                        "link": "/admin/django_cfg_accounts/registrationsource/",
                    },
                    {
                        "title": "User Registration Sources",
                        "icon": "person",
                        "link": "/admin/django_cfg_accounts/userregistrationsource/",
                    },
                ]
            })
        
        # Add Support section if enabled
        if self.is_support_enabled():
            navigation.append({
                "title": "Support",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Tickets",
                        "icon": "support_agent",
                        "link": "/admin/django_cfg_support/ticket/",
                    },
                    {
                        "title": "Messages",
                        "icon": "chat",
                        "link": "/admin/django_cfg_support/message/",
                    },
                ]
            })
        
        # Add Newsletter section if enabled
        if self.is_newsletter_enabled():
            navigation.append({
                "title": "Newsletter",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Newsletters",
                        "icon": "email",
                        "link": "/admin/django_cfg_newsletter/newsletter/",
                    },
                    {
                        "title": "Subscriptions",
                        "icon": "person_add",
                        "link": "/admin/django_cfg_newsletter/newslettersubscription/",
                    },
                    {
                        "title": "Campaigns",
                        "icon": "campaign",
                        "link": "/admin/django_cfg_newsletter/newslettercampaign/",
                    },
                    {
                        "title": "Email Logs",
                        "icon": "mail_outline",
                        "link": "/admin/django_cfg_newsletter/emaillog/",
                    },
                ]
            })
        
        # Add Leads section if enabled
        if self.is_leads_enabled():
            navigation.append({
                "title": "Leads",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Leads",
                        "icon": "contact_page",
                        "link": "/admin/django_cfg_leads/lead/",
                    },
                ]
            })
        
        return navigation
    
    def _get_reverse_lazy(self, link: str) -> str:
        """Safe reverse with fallback."""
        try:
            from django.urls import reverse
            return reverse(link)
        except Exception:
            return link
    
    
    def _get_user_admin_url(self) -> str:
        """Get admin changelist URL for the current AUTH_USER_MODEL."""
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            app_label = User._meta.app_label
            model_name = User._meta.model_name
            # Return string URL, not reverse_lazy object
            return f'/admin/{app_label}/{model_name}/'
        except Exception:
            # Universal fallback - return admin index instead of hardcoded model
            return '/admin/'
    
    def get_unfold_config(self) -> Dict[str, Any]:
        """Get complete Unfold configuration based on working old version."""
        return {
            # Site branding and appearance
            "SITE_TITLE": "Admin",
            "SITE_HEADER": "Admin",
            "SITE_SUBHEADER": "",
            "SITE_URL": "/",
            "SITE_SYMBOL": "dashboard",
            
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
                "redirect_after": lambda request: "/admin/",
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
            
            # Sidebar navigation - KEY STRUCTURE!
            "SIDEBAR": {
                "show_search": True,
                "command_search": True,
                "show_all_applications": True,
                "navigation": self.get_navigation_config(),
            },
            
            # Site dropdown menu - moved to top level
            "SITE_DROPDOWN": [
                # {
                #     "icon": "language",
                #     "title": "Documentation",
                #     "link": "https://docs.carapis.com",
                # },
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
