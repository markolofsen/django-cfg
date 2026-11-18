"""
Django CFG Unfold Module

Provides complete Unfold admin interface integration with
navigation and theming support.
"""

from .models import *
from .navigation import NavBuilder, NavigationManager, get_navigation_manager
from .tailwind import get_css_variables, get_unfold_colors

# Export main components
__all__ = [
    'NavigationManager',
    'get_navigation_manager',
    'NavBuilder',
    'get_unfold_colors',
    'get_css_variables',
    # Models
    'UnfoldConfig',
    'UnfoldTheme',
    'UnfoldSidebar',
    'UnfoldThemeConfig',
    'UnfoldDashboardConfig',
    'NavigationItem',
    'NavigationSection',
    'NavigationItemType',
    'SiteDropdownItem',
]

# Version info
__version__ = '1.0.0'
__author__ = 'Django CFG Team'
__email__ = 'team@djangocfg.com'

# Module metadata
__title__ = 'Django CFG Unfold'
__description__ = 'Complete Unfold admin interface integration'
__url__ = 'https://github.com/djangocfg/django-cfg'
