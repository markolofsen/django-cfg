"""
Django-CFG Library Configuration

Configuration settings for the django-cfg library itself.
"""

from typing import List
from .modules.django_unfold.icons import Icons
from .modules.django_unfold.models.dropdown import SiteDropdownItem


# Library configuration
LIB_NAME = "Django CFG"
LIB_SITE_URL = "https://djangocfg.com"
LIB_DOCS_URL = "https://docs.djangocfg.com"
LIB_GITHUB_URL = "https://github.com/django-cfg/django-cfg"
LIB_SUPPORT_URL = "https://djangocfg.com/support"
LIB_HEALTH_URL = "/cfg/health/"

def get_maintenance_url(domain: str) -> str:
    """Get the maintenance URL for the current site."""
    # return f"{LIB_SITE_URL}/maintenance/{domain}/"
    return f"{LIB_DOCS_URL}/maintenance?site={domain}"

def get_default_dropdown_items() -> List[SiteDropdownItem]:
    """Get default dropdown menu items for Unfold admin."""
    return [
        SiteDropdownItem(
            title="Documentation",
            icon=Icons.HELP_OUTLINE,
            link=LIB_DOCS_URL,
        ),
        SiteDropdownItem(
            title="GitHub",
            icon=Icons.CODE,
            link=LIB_GITHUB_URL,
        ),
        SiteDropdownItem(
            title="Support",
            icon=Icons.SUPPORT_AGENT,
            link=LIB_SUPPORT_URL,
        ),
        SiteDropdownItem(
            title="Django-CFG",
            icon=Icons.HOME,
            link=LIB_SITE_URL,
        ),
    ]
