"""
Field configuration for declarative admin.

Type-safe field configurations with widget-specific classes.
"""

from typing import Annotated, Any, Union

from pydantic import Discriminator, Tag

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
from .money import MoneyFieldDisplay
from .short_uuid import ShortUUIDField
from .stacked import RowItem, StackedField
from .status_badges import BadgeRule, StatusBadgesField
from .text import TextField
from .toon import ToonField
from .user import UserField
from .video import VideoField


def _get_field_type(v: Any) -> str:
    """Discriminator function for FieldConfigType."""
    if isinstance(v, ToonField):
        return "toon"
    if isinstance(v, BadgeField):
        return "badge"
    if isinstance(v, CurrencyField):
        return "currency"
    if isinstance(v, DateTimeField):
        return "datetime"
    if isinstance(v, UserField):
        return "user"
    if isinstance(v, TextField):
        return "text"
    if isinstance(v, BooleanField):
        return "boolean"
    if isinstance(v, ImagePreviewField):
        return "image_preview"
    if isinstance(v, ImageField):
        return "image"
    if isinstance(v, MarkdownField):
        return "markdown"
    if isinstance(v, MoneyFieldDisplay):
        return "money"
    if isinstance(v, LinkField):
        return "link"
    if isinstance(v, StatusBadgesField):
        return "status_badges"
    if isinstance(v, CounterBadgeField):
        return "counter_badge"
    if isinstance(v, DecimalField):
        return "decimal"
    if isinstance(v, AvatarField):
        return "avatar"
    if isinstance(v, ShortUUIDField):
        return "short_uuid"
    if isinstance(v, VideoField):
        return "video"
    if isinstance(v, ForeignKeyField):
        return "foreignkey"
    if isinstance(v, StackedField):
        return "stacked"
    return "base"


# Discriminated union of all concrete field config types.
# Use this instead of FieldConfig for precise type narrowing.
FieldConfigType = Annotated[
    Union[
        Annotated[BadgeField, Tag("badge")],
        Annotated[CurrencyField, Tag("currency")],
        Annotated[DateTimeField, Tag("datetime")],
        Annotated[UserField, Tag("user")],
        Annotated[TextField, Tag("text")],
        Annotated[BooleanField, Tag("boolean")],
        Annotated[ImagePreviewField, Tag("image_preview")],
        Annotated[ImageField, Tag("image")],
        Annotated[MarkdownField, Tag("markdown")],
        Annotated[MoneyFieldDisplay, Tag("money")],
        Annotated[LinkField, Tag("link")],
        Annotated[StatusBadgesField, Tag("status_badges")],
        Annotated[CounterBadgeField, Tag("counter_badge")],
        Annotated[DecimalField, Tag("decimal")],
        Annotated[AvatarField, Tag("avatar")],
        Annotated[ShortUUIDField, Tag("short_uuid")],
        Annotated[VideoField, Tag("video")],
        Annotated[ForeignKeyField, Tag("foreignkey")],
        Annotated[StackedField, Tag("stacked")],
        Annotated[ToonField, Tag("toon")],
        Annotated[FieldConfig, Tag("base")],
    ],
    Discriminator(_get_field_type),
]

__all__ = [
    "FieldConfig",
    "FieldConfigType",
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
    "MoneyFieldDisplay",
    "ShortUUIDField",
    "LinkField",
    "ForeignKeyField",
    "AvatarField",
    "StackedField",
    "RowItem",
    "StatusBadgesField",
    "BadgeRule",
    "CounterBadgeField",
    "VideoField",
    "ToonField",
]
