"""
Unfold Dashboard Models Package

Extended Pydantic models for Unfold admin dashboard configuration.
These are separate from the main UnfoldConfig in unfold.py.
"""

from .navigation import NavigationItem, NavigationSection, NavigationItemType
from .dropdown import SiteDropdownItem
from .tabs import TabConfiguration
from .dashboard import StatCard, SystemHealthItem, QuickAction, DashboardData
from .config import UnfoldConfig, UnfoldDashboardConfig

__all__ = [
    # Main configs
    "UnfoldConfig",
    "UnfoldDashboardConfig",
    
    # Navigation models
    "NavigationItem",
    "NavigationSection", 
    "NavigationItemType",
    
    # Dropdown models
    "SiteDropdownItem",
    
    # Tab models
    "TabConfiguration",
    
    # Dashboard components
    "StatCard",
    "SystemHealthItem",
    "QuickAction",
    "DashboardData",
]
