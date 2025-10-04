"""
Shared admin actions for knowbase.

Provides reusable actions for admin interfaces.
"""

from .visibility_actions import VisibilityActions, mark_as_public, mark_as_private

__all__ = [
    'VisibilityActions',
    'mark_as_public',
    'mark_as_private',
]
