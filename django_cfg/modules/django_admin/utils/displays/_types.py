"""
TypedDicts for display class config parameters.

Replace raw Dict[str, Any] config bags with typed configs.
"""
from __future__ import annotations

from typing import Dict, Literal, Optional, TypedDict


class CountryDisplayConfig(TypedDict, total=False):
    show_flag: bool   # default True
    show_name: bool   # default True
    show_code: bool   # default False


class CityDisplayConfig(TypedDict, total=False):
    show_flag: bool         # default True
    show_state: bool        # default True
    show_country: bool      # default True
    show_coordinates: bool  # default False


class CoordinatesDisplayConfig(TypedDict, total=False):
    lat_field: str   # default "latitude"
    lon_field: str   # default "longitude"
    precision: int   # default 4
    show_link: bool  # default False


class TextRendererConfig(TypedDict, total=False):
    bold: bool
    muted: bool
    monospace: bool
    prefix: Optional[str]
    suffix: Optional[str]
    truncate: Optional[int]
    icon: Optional[str]
    hide_if_empty: bool


class BadgeRendererConfig(TypedDict, total=False):
    variant: Literal["primary", "secondary", "success", "danger", "warning", "info"]
    label_map: Dict[str, str]
    true_label: Optional[str]
    false_label: Optional[str]
    icon: Optional[str]


class DateTimeItemConfig(TypedDict, total=False):
    muted: bool          # default True
    show_relative: bool  # default False


class MoneyItemConfig(TypedDict, total=False):
    currency: str
    decimal_places: int
    smart_decimal_places: bool
    show_currency_symbol: bool
    thousand_separator: bool


__all__ = [
    "CountryDisplayConfig",
    "CityDisplayConfig",
    "CoordinatesDisplayConfig",
    "TextRendererConfig",
    "BadgeRendererConfig",
    "DateTimeItemConfig",
    "MoneyItemConfig",
]
