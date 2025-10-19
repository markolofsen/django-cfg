"""
Unfold Models Package

All Pydantic models for Django Unfold admin interface.
"""

from .config import (
    UnfoldColors,
    UnfoldConfig,
    UnfoldDashboardConfig,
    UnfoldSidebar,
    UnfoldTheme,
    UnfoldThemeConfig,
)
from .dashboard import (
    ChartData,
    ChartDataset,
    DashboardData,
    DashboardWidget,
    QuickAction,
    StatCard,
    SystemHealthItem,
)
from .dropdown import SiteDropdownItem
from .navigation import NavigationItem, NavigationItemType, NavigationSection
from .tabs import TabConfiguration, TabItem

__all__ = [
    # Config models
    'UnfoldConfig',
    'UnfoldTheme',
    'UnfoldColors',
    'UnfoldSidebar',
    'UnfoldThemeConfig',
    'UnfoldDashboardConfig',

    # Navigation models
    'NavigationItem',
    'NavigationSection',
    'NavigationItemType',

    # Dropdown models
    'SiteDropdownItem',

    # Dashboard models
    'StatCard',
    'SystemHealthItem',
    'QuickAction',
    'DashboardWidget',
    'DashboardData',
    'ChartDataset',
    'ChartData',

    # Tab models
    'TabConfiguration',
    'TabItem',
]
