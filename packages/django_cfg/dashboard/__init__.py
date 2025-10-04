"""
Django CFG Dashboard Module.

Section-based architecture for dashboard rendering.
Inspired by Unfold's clean component approach.
"""

from .sections.base import DashboardSection
from .sections.overview import OverviewSection
from .sections.stats import StatsSection
from .sections.system import SystemSection
from .sections.commands import CommandsSection

# Import components to register them with Unfold
# The @register_component decorator runs on import
from . import components  # noqa: F401

__all__ = [
    'DashboardSection',
    'OverviewSection',
    'StatsSection',
    'SystemSection',
    'CommandsSection',
]
