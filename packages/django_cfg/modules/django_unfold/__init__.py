"""
Django CFG Unfold Module

Provides complete Unfold admin interface integration with
navigation and theming support.
"""

from .models import *
from .navigation import NavigationManager, get_navigation_manager
from .system_monitor import SystemMonitor
from .tailwind import get_css_variables, get_unfold_colors


# Lazy initialization functions to avoid circular imports
def get_system_monitor() -> SystemMonitor:
    """Get the global system monitor instance."""
    global _system_monitor
    if '_system_monitor' not in globals():
        globals()['_system_monitor'] = SystemMonitor()
    return globals()['_system_monitor']

# Export main components
__all__ = [
    'NavigationManager',
    'get_navigation_manager',
    'SystemMonitor',
    'get_system_monitor',
    'get_unfold_colors',
    'get_css_variables',
    # Models
    'UnfoldConfig',
    'UnfoldTheme',
    'UnfoldColors',
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
