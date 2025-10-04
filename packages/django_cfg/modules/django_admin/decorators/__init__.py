"""
Django Admin Decorators - Wrappers for Unfold decorators.

Provides consistent, type-safe decorators with our admin utilities integration.
"""

from .display import display
from .actions import action

__all__ = [
    'display',
    'action',
]
