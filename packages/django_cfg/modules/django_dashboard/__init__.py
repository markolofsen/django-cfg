"""
Django CFG Dashboard Module.

Section-based architecture for dashboard rendering.
Inspired by Unfold's clean component approach.
"""

# Import components to register them with Unfold
# The @register_component decorator runs on import
from . import components  # noqa: F401
from .sections.base import DashboardSection
from .sections.commands import CommandsSection
from .sections.overview import OverviewSection
from .sections.stats import StatsSection
from .sections.system import SystemSection

__all__ = [
    'DashboardSection',
    'OverviewSection',
    'StatsSection',
    'SystemSection',
    'CommandsSection',
]
