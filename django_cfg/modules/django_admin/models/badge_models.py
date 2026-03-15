"""
Badge configuration models.
"""

from typing import Any, Dict, Optional, Union

from pydantic import Field, field_validator

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

    @field_validator('custom_mappings', mode='before')
    @classmethod
    def normalize_mappings(cls, v: Any) -> Dict[str, str]:
        """Convert boolean keys to strings for compatibility."""
        if not isinstance(v, dict):
            return {}
        result = {}
        for key, value in v.items():
            # Convert bool keys to lowercase strings
            if isinstance(key, bool):
                key = 'true' if key else 'false'
            result[str(key)] = value
        return result
