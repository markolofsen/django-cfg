"""
Base Pydantic 2 models.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List
from enum import Enum


class BaseConfig(BaseModel):
    """Base configuration for all utilities."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    cache_timeout: int = Field(default=300, ge=0, le=3600)
    enable_icons: bool = Field(default=True)
    debug_mode: bool = Field(default=False)


class BadgeVariant(str, Enum):
    """Badge color variants."""
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    INFO = "info"
    PRIMARY = "primary"
    SECONDARY = "secondary"
