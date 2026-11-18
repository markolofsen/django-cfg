"""
Action configuration models.
"""

from enum import Enum
from typing import List, Optional

from pydantic import Field

from .base import BaseConfig


class ActionVariant(str, Enum):
    """
    Action variant enum: the button style, rendered as ``cfg-action-<value>``.
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
