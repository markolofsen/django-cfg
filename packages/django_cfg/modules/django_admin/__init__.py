"""
Django Admin Utilities - Universal HTML Builder System

Clean, type-safe admin utilities with no HTML duplication.
"""

# Core utilities
from .utils.displays import UserDisplay, MoneyDisplay, StatusDisplay, DateTimeDisplay
from .utils.badges import StatusBadge, ProgressBadge, CounterBadge

# Icons
from .icons import Icons, IconCategories

# Admin mixins
from .mixins.display_mixin import DisplayMixin
from .mixins.optimization_mixin import OptimizedModelAdmin
from .mixins.standalone_actions_mixin import StandaloneActionsMixin, standalone_action

# Configuration models
from .models.display_models import UserDisplayConfig, MoneyDisplayConfig, DateTimeDisplayConfig
from .models.badge_models import BadgeConfig, BadgeVariant, StatusBadgeConfig
from .models.action_models import ActionVariant, ActionConfig

# Decorators
from .decorators import display, action

__version__ = "1.0.0"

__all__ = [
    # Display utilities
    "UserDisplay",
    "MoneyDisplay", 
    "StatusDisplay",
    "DateTimeDisplay",
    
    # Badge utilities
    "StatusBadge",
    "ProgressBadge",
    "CounterBadge",
    
    # Icons
    "Icons",
    "IconCategories",
    
    # Admin mixins
    "OptimizedModelAdmin",
    "DisplayMixin",
    "StandaloneActionsMixin",
    "standalone_action",
    
    # Configuration models
    "UserDisplayConfig",
    "MoneyDisplayConfig",
    "DateTimeDisplayConfig",
    "BadgeConfig",
    "BadgeVariant",
    "StatusBadgeConfig",
    "ActionVariant",
    "ActionConfig",
    
    # Decorators
    "display",
    "action",
]
