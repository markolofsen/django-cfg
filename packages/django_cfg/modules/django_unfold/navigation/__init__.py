"""
Navigation package for Django Unfold.

Public API (backward-compatible with previous navigation.py):
    from django_cfg.modules.django_unfold.navigation import NavigationManager, get_navigation_manager

NavBuilder is also exported for use in extensions or custom navigation sections:
    from django_cfg.modules.django_unfold.navigation import NavBuilder
"""

from .builder import NavBuilder
from .manager import NavigationManager, get_navigation_manager

__all__ = [
    "NavBuilder",
    "NavigationManager",
    "get_navigation_manager",
]
