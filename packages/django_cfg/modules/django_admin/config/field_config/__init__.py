"""
Field configuration for declarative admin.

Type-safe field configurations with widget-specific classes.
"""

from .avatar import AvatarField
from .badge import BadgeField
from .base import FieldConfig
from .boolean import BooleanField
from .counter_badge import CounterBadgeField
from .currency import CurrencyField
from .datetime import DateTimeField
from .decimal import DecimalField
from .image import ImageField
from .link import LinkField
from .markdown import MarkdownField
from .short_uuid import ShortUUIDField
from .status_badges import BadgeRule, StatusBadgesField
from .text import TextField
from .user import UserField

__all__ = [
    "FieldConfig",
    "BadgeField",
    "CurrencyField",
    "DateTimeField",
    "DecimalField",
    "UserField",
    "TextField",
    "BooleanField",
    "ImageField",
    "MarkdownField",
    "ShortUUIDField",
    "LinkField",
    "AvatarField",
    "StatusBadgesField",
    "BadgeRule",
    "CounterBadgeField",
]
