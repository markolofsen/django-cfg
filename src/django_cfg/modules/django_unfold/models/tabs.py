"""
Tab Configuration Models for Unfold Dashboard

Pydantic models for tab configurations.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class TabItem(BaseModel):
    """Tab item configuration."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    title: str = Field(..., min_length=1, description="Tab title")
    link: str = Field(..., min_length=1, description="Tab URL")
    permission: Optional[str] = Field(None, description="Permission callback")


class TabConfiguration(BaseModel):
    """Tab configuration for admin models."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    models: List[str] = Field(..., min_items=1, description="Model names for tab")
    items: List[TabItem] = Field(..., min_items=1, description="Tab items")
