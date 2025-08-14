"""
Tab Configuration Models for Unfold Dashboard

Pydantic models for tab configurations.
"""

from typing import List
from pydantic import BaseModel, Field, ConfigDict
from .navigation import NavigationItem


class TabConfiguration(BaseModel):
    """Tab configuration for admin models."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    models: List[str] = Field(..., min_items=1, description="Model names for tab")
    items: List[NavigationItem] = Field(..., min_items=1, description="Tab items")
