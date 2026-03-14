"""
TypedDicts for WidgetRegistry handler configs.

Each widget registration passes a config dict — these TypedDicts document
and type that contract.
"""
from __future__ import annotations

from typing import Dict, Literal, Optional, TypedDict


class UserHandlerConfig(TypedDict, total=False):
    show_email: bool
    show_avatar: bool
    avatar_size: int
    is_link: bool  # internal key, filtered before passing to UserDisplayConfig


class MoneyHandlerConfig(TypedDict, total=False):
    currency: str
    decimal_places: int
    smart_decimal_places: bool
    rate_mode: bool
    show_sign: bool
    show_currency_symbol: bool
    thousand_separator: bool
    is_link: bool


class MoneyBreakdownHandlerConfig(MoneyHandlerConfig, total=False):
    breakdown_items: list[dict]  # list of {label, amount, color}


class MoneyFieldHandlerConfig(TypedDict, total=False):
    field_names: Dict[str, str]  # {"amount": fname, "currency": fname, ...}
    target_currency: str
    default_currency: str
    show_rate: bool
    precision: int
    compact: bool
    currency_symbols: Dict[str, str]
    is_link: bool


class BadgeHandlerConfig(TypedDict, total=False):
    variant: Literal["primary", "secondary", "success", "danger", "warning", "info"]
    custom_mappings: Dict[str, str]
    icon: Optional[str]
    is_link: bool


class CounterHandlerConfig(TypedDict, total=False):
    label: Optional[str]
    is_link: bool


class DateTimeHandlerConfig(TypedDict, total=False):
    datetime_format: Optional[str]
    show_relative: bool
    use_local_tz: bool
    is_link: bool


class BooleanHandlerConfig(TypedDict, total=False):
    true_icon: Optional[str]
    false_icon: Optional[str]
    is_link: bool


class MarkdownHandlerConfig(TypedDict, total=False):
    collapsible: bool
    title: str
    header_icon: str
    max_height: str
    enable_plugins: bool
    default_open: bool
    is_link: bool


class GeoHandlerConfig(TypedDict, total=False):
    show_flag: bool
    show_name: bool
    show_code: bool
    show_state: bool
    show_country: bool
    show_coordinates: bool
    is_link: bool


class DecimalHandlerConfig(TypedDict, total=False):
    decimal_places: int
    prefix: Optional[str]
    suffix: Optional[str]
    is_link: bool


class TextHandlerConfig(TypedDict, total=False):
    bold: bool
    muted: bool
    monospace: bool
    prefix: Optional[str]
    suffix: Optional[str]
    truncate: Optional[int]
    icon: Optional[str]
    is_link: bool


class ToonHandlerConfig(TypedDict, total=False):
    preview_lines: int
    default_mode: Literal["toon", "json"]
    collapsible: bool
    default_open: bool
    label: Optional[str]
    max_height: str
    is_link: bool


__all__ = [
    "UserHandlerConfig",
    "MoneyHandlerConfig",
    "MoneyBreakdownHandlerConfig",
    "MoneyFieldHandlerConfig",
    "BadgeHandlerConfig",
    "CounterHandlerConfig",
    "DateTimeHandlerConfig",
    "BooleanHandlerConfig",
    "MarkdownHandlerConfig",
    "GeoHandlerConfig",
    "DecimalHandlerConfig",
    "TextHandlerConfig",
    "ToonHandlerConfig",
]
