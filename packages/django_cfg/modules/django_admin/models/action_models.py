"""
Action configuration models.
"""

from enum import Enum
from typing import List, Optional

from pydantic import Field

from .base import BaseConfig


class ActionVariant(str, Enum):
    """
    Action variant enum for consistent styling.
    
    Based on Unfold ActionVariant but with our own namespace.
    Matches unfold.enums.ActionVariant exactly.
    """
    DEFAULT = "default"
    PRIMARY = "primary"
    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"
    DANGER = "danger"


class ActionConfig(BaseConfig):
    """Action configuration."""
    variant: ActionVariant = Field(default=ActionVariant.PRIMARY)
    icon: Optional[str] = Field(default=None)
    permissions: List[str] = Field(default=[])
    confirm_message: Optional[str] = Field(default=None)
    success_message: Optional[str] = Field(default=None)
    error_message: Optional[str] = Field(default=None)
