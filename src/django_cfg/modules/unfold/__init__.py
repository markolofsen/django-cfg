"""
Django CFG Unfold Module

Complete Unfold admin interface integration with system monitoring,
dashboard callbacks, and auto-configuration.
"""

from .system_monitor import SystemMonitor
from .dashboard import DashboardManager
from .callbacks import UnfoldCallbacks
from .models import DashboardData, StatCard, SystemHealthItem, QuickAction

# Export instances for easy import
system_monitor = SystemMonitor()
dashboard_manager = DashboardManager()
unfold_callbacks = UnfoldCallbacks()

__all__ = [
    "SystemMonitor",
    "DashboardManager", 
    "UnfoldCallbacks",
    "DashboardData",
    "StatCard",
    "SystemHealthItem",
    "QuickAction",
    "system_monitor",
    "dashboard_manager",
    "unfold_callbacks",
]
