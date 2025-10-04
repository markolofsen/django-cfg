"""
Admin mixins for easy integration.
"""

from .display_mixin import DisplayMixin
from .optimization_mixin import OptimizedModelAdmin
from .standalone_actions_mixin import StandaloneActionsMixin, standalone_action

__all__ = [
    "DisplayMixin",
    "OptimizedModelAdmin",
    "StandaloneActionsMixin",
    "standalone_action",
]
