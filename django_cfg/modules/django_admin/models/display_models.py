"""
Display configuration models.
"""

from pydantic import Field

from .base import BaseConfig


class UserDisplayConfig(BaseConfig):
    """User display configuration."""
    show_email: bool = Field(default=True)
    show_avatar: bool = Field(default=True)
    avatar_size: int = Field(default=32, ge=16, le=128)


class MoneyDisplayConfig(BaseConfig):
    """Money display configuration."""
    currency: str = Field(default="USD", min_length=3, max_length=3)
    show_sign: bool = Field(default=True)
    decimal_places: int = Field(default=2, ge=0, le=8)
    thousand_separator: bool = Field(default=True)
    show_currency_symbol: bool = Field(default=True)
    smart_decimal_places: bool = Field(default=False)  # Auto-adjust decimal places based on value
    rate_mode: bool = Field(default=False)  # Special formatting for exchange rates


class DateTimeDisplayConfig(BaseConfig):
    """DateTime display configuration."""
    show_relative: bool = Field(default=True)
    show_seconds: bool = Field(default=False)
    datetime_format: str = Field(default="%Y-%m-%d %H:%M:%S")
    use_local_tz: bool = Field(default=True, description="Convert to local timezone (default: True)")
