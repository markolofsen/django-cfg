"""
Django CFG Unfold Module

Provides complete Unfold admin interface integration with dashboard,
navigation, theming, and callback support.
"""

from .dashboard import DashboardManager, get_dashboard_manager
from .callbacks import UnfoldCallbacks
from .system_monitor import SystemMonitor
from .tailwind import get_unfold_colors, get_css_variables
from .models import *

# Lazy initialization functions to avoid circular imports
def get_system_monitor() -> SystemMonitor:
    """Get the global system monitor instance."""
    global _system_monitor
    if '_system_monitor' not in globals():
        globals()['_system_monitor'] = SystemMonitor()
    return globals()['_system_monitor']

def get_unfold_callbacks() -> UnfoldCallbacks:
    """Get the global unfold callbacks instance."""
    global _unfold_callbacks
    if '_unfold_callbacks' not in globals():
        globals()['_unfold_callbacks'] = UnfoldCallbacks()
    return globals()['_unfold_callbacks']

# Export main components
__all__ = [
    'DashboardManager',
    'get_dashboard_manager',
    'UnfoldCallbacks', 
    'get_unfold_callbacks',
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
    'StatCard',
    'SystemHealthItem',
    'QuickAction',
    'DashboardWidget',
    'DashboardData',
    'ChartDataset',
    'ChartData',
    'TabConfiguration',
    'TabItem',
]

# Version info
__version__ = '1.0.0'
__author__ = 'Django CFG Team'
__email__ = 'team@djangocfg.com'

# Module metadata
__title__ = 'Django CFG Unfold'
__description__ = 'Complete Unfold admin interface integration'
__url__ = 'https://github.com/djangocfg/django-cfg'