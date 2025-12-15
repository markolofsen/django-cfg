"""
Django Admin for Web Push models.

Uses PydanticAdmin with declarative configuration.
"""

from .config import pushsubscription_config
from .push_subscription import PushSubscriptionAdmin

__all__ = [
    "pushsubscription_config",
    "PushSubscriptionAdmin",
]
