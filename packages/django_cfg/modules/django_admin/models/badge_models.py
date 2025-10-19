"""
Badge configuration models.
"""

from typing import Dict, Optional

from pydantic import Field

from .base import BadgeVariant, BaseConfig


class BadgeConfig(BaseConfig):
    """Base badge configuration."""
    variant: BadgeVariant = Field(default=BadgeVariant.INFO)
    icon: Optional[str] = Field(default=None)
    css_classes: list = Field(default=[])


class StatusBadgeConfig(BadgeConfig):
    """Status badge configuration."""
    custom_mappings: Dict[str, str] = Field(default={})
    show_icons: bool = Field(default=True)
