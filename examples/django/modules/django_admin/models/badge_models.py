"""
Badge configuration models.
"""

from pydantic import Field
from typing import Optional, Dict
from .base import BaseConfig, BadgeVariant


class BadgeConfig(BaseConfig):
    """Base badge configuration."""
    variant: BadgeVariant = Field(default=BadgeVariant.INFO)
    icon: Optional[str] = Field(default=None)
    css_classes: list = Field(default=[])


class StatusBadgeConfig(BadgeConfig):
    """Status badge configuration."""
    custom_mappings: Dict[str, str] = Field(default={})
    show_icons: bool = Field(default=True)
