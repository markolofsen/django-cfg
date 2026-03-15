"""
TypedDicts for FieldConfig.get_widget_config() return values.

Each FieldConfig subclass returns one of these typed dicts.
Replace raw Dict[str, Any] return types on get_widget_config().
"""
from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, TypedDict


class BaseWidgetConfig(TypedDict, total=False):
    name: str
    title: Optional[str]
    icon: Optional[str]
    empty_value: str
    is_link: bool
    field_id: str   # injected at render time


class BadgeWidgetConfig(BaseWidgetConfig, total=False):
    variant: str
    custom_mappings: Dict[Any, str]


class BooleanWidgetConfig(BaseWidgetConfig, total=False):
    true_icon: str
    false_icon: str


class CurrencyWidgetConfig(BaseWidgetConfig, total=False):
    currency: str
    decimal_places: int
    smart_decimal_places: bool
    rate_mode: bool
    show_sign: bool
    show_currency_symbol: bool
    thousand_separator: bool


class DateTimeWidgetConfig(BaseWidgetConfig, total=False):
    datetime_format: str
    show_relative: bool
    use_local_tz: bool


class UserWidgetConfig(BaseWidgetConfig, total=False):
    show_email: bool
    show_avatar: bool
    avatar_size: int


class TextWidgetConfig(BaseWidgetConfig, total=False):
    bold: bool
    muted: bool
    monospace: bool
    prefix: Optional[str]
    suffix: Optional[str]
    truncate: Optional[int]
    link_field: Optional[str]
    link_url_template: Optional[str]
    link_text: Optional[str]


class DecimalWidgetConfig(BaseWidgetConfig, total=False):
    decimal_places: int
    prefix: Optional[str]
    suffix: Optional[str]


class ImageWidgetConfig(BaseWidgetConfig, total=False):
    thumbnail_width: str
    thumbnail_height: str
    show_info: bool
    zoom_enabled: bool


class MarkdownWidgetConfig(BaseWidgetConfig, total=False):
    collapsible: bool
    default_open: bool
    max_height: str
    header_icon: Optional[str]
    enable_plugins: bool
    full_width: bool


class LinkWidgetConfig(BaseWidgetConfig, total=False):
    url_field: Optional[str]
    url_template: Optional[str]
    link_text: Optional[str]
    open_in_new_tab: bool
    show_icon: bool


class AvatarWidgetConfig(BaseWidgetConfig, total=False):
    size: str
    shape: Literal["circle", "square"]
    fallback_initials_field: Optional[str]


class ShortUUIDWidgetConfig(BaseWidgetConfig, total=False):
    chars: int
    monospace: bool
    copy_button: bool


class VideoWidgetConfig(BaseWidgetConfig, total=False):
    thumbnail_width: str
    thumbnail_height: str
    show_duration: bool


class ForeignKeyWidgetConfig(BaseWidgetConfig, total=False):
    display_field: Optional[str]
    link_to_admin: bool


class StatusBadgesWidgetConfig(BaseWidgetConfig, total=False):
    rules: List[Dict[str, Any]]


class CounterBadgeWidgetConfig(BaseWidgetConfig, total=False):
    label: Optional[str]
    color: str
    size: str


class MoneyFieldWidgetConfig(BaseWidgetConfig, total=False):
    field_names: Dict[str, str]
    target_currency: str
    default_currency: str
    show_rate: bool
    precision: int
    compact: bool
    currency_symbols: Dict[str, str]


class StackedWidgetConfig(BaseWidgetConfig, total=False):
    rows: List[Any]   # serialized RowItem / list of RowItem
    gap: str
    inline_gap: str
    align: Literal["left", "center", "right"]
    min_width: Optional[str]
    max_width: str


class ToonWidgetConfig(BaseWidgetConfig, total=False):
    collapsible: bool
    default_open: bool
    default_mode: Literal["toon", "json"]
    preview_lines: int
    label: Optional[str]
    max_height: str


__all__ = [
    "BaseWidgetConfig",
    "BadgeWidgetConfig",
    "BooleanWidgetConfig",
    "CurrencyWidgetConfig",
    "DateTimeWidgetConfig",
    "UserWidgetConfig",
    "TextWidgetConfig",
    "DecimalWidgetConfig",
    "ImageWidgetConfig",
    "MarkdownWidgetConfig",
    "LinkWidgetConfig",
    "AvatarWidgetConfig",
    "ShortUUIDWidgetConfig",
    "VideoWidgetConfig",
    "ForeignKeyWidgetConfig",
    "StatusBadgesWidgetConfig",
    "CounterBadgeWidgetConfig",
    "MoneyFieldWidgetConfig",
    "StackedWidgetConfig",
    "ToonWidgetConfig",
]
