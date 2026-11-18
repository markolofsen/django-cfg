"""
The django-cfg admin site: the stock Django ``AdminSite`` with our navigation and branding.

``AdminSiteConfig`` and the navigation models feed ``CfgAdminSite`` (``site.py``),
installed by ``CfgAdminConfig`` (``apps.py``). The package exports the models only:
``navigation`` (the django-cfg sidebar sections) is imported when the sidebar is
built, not by ``import django_cfg``.
"""

from .models import *

__all__ = [
    'AdminSiteConfig',
    'AdminSidebar',
    'NavigationItem',
    'NavigationSection',
    'NavigationItemType',
    'SiteDropdownItem',
]
