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
from .foreignkey import ForeignKeyField
from .image import ImageField
from .image_preview import ImagePreviewField
from .link import LinkField
from .markdown import MarkdownField
from .short_uuid import ShortUUIDField
from .status_badges import BadgeRule, StatusBadgesField
from .text import TextField
from .user import UserField
from .video import VideoField

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
    "ImagePreviewField",
    "MarkdownField",
    "ShortUUIDField",
    "LinkField",
    "ForeignKeyField",
    "AvatarField",
    "StatusBadgesField",
    "BadgeRule",
    "CounterBadgeField",
    "VideoField",
]
