"""
Display utilities for Django Admin.

Provides display classes for various field types.
"""

from .avatar_display import AvatarDisplay
from .counter_badge_display import CounterBadgeDisplay
from .boolean_display import BooleanDisplay
from .datetime_display import DateTimeDisplay
from .money_display import MoneyDisplay
from .user_display import UserDisplay
from .decimal_display import DecimalDisplay
from .image_display import ImageDisplay
from .image_preview import ImagePreviewDisplay
from .json_display import JSONDisplay
from .link_display import LinkDisplay
from .short_uuid_display import ShortUUIDDisplay
from .status_badges_display import StatusBadgesDisplay
from .text_display import TextDisplay
from .stacked import StackedDisplay
from .video_display import VideoDisplay
from .geo import CityDisplay, CoordinatesDisplay, CountryDisplay, LocationDisplay
from .toon_display import ToonDisplay

__all__ = [
    "UserDisplay",
    "MoneyDisplay",
    "DateTimeDisplay",
    "BooleanDisplay",
    "DecimalDisplay",
    "ImageDisplay",
    "ImagePreviewDisplay",
    "JSONDisplay",
    "AvatarDisplay",
    "LinkDisplay",
    "StatusBadgesDisplay",
    "CounterBadgeDisplay",
    "ShortUUIDDisplay",
    "StackedDisplay",
    "TextDisplay",
    "VideoDisplay",
    "ToonDisplay",
    # Geo displays
    "CountryDisplay",
    "CityDisplay",
    "LocationDisplay",
    "CoordinatesDisplay",
]
