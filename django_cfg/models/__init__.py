"""
Configuration Models

Type-safe Pydantic 2 models for Django configuration.
"""

from .base import BaseConfig
from .environment import EnvironmentConfig
from .database import DatabaseConfig
from .security import SecurityConfig
from .api import APIConfig
from .cache import CacheConfig
from .email import EmailConfig
from .constance import ConstanceConfig, ConstanceFieldConfig
from .logging import LoggingConfig, LoggerConfig, HandlerConfig, FormatterConfig

# Import all Unfold models from consolidated unfold package
from .unfold import (
    UnfoldConfig,
    UnfoldDashboardConfig,
    NavigationItem,
    NavigationSection,
    NavigationItemType,
    SiteDropdownItem,
    TabConfiguration,
    StatCard,
    SystemHealthItem,
    QuickAction,
    DashboardData,
)

__all__ = [
    # Base
    "BaseConfig",
    # Core models
    "EnvironmentConfig",
    "DatabaseConfig",
    "SecurityConfig",
    "APIConfig",
    "CacheConfig",
    "EmailConfig",
    # Extended models
    "UnfoldConfig",
    # New Unfold dashboard models
    "UnfoldDashboardConfig",
    "NavigationItem",
    "NavigationSection",
    "NavigationItemType",
    "SiteDropdownItem",
    "TabConfiguration",
    "StatCard",
    "SystemHealthItem",
    "QuickAction",
    "DashboardData",
    "ConstanceConfig",
    "ConstanceFieldConfig",
    "LoggingConfig",
    "LoggerConfig",
    "HandlerConfig",
    "FormatterConfig",
]
