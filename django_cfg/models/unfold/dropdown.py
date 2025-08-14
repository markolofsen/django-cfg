"""
Site Dropdown Models for Unfold Dashboard

Pydantic models for site dropdown menu items.
"""

from pydantic import BaseModel, Field, ConfigDict


class SiteDropdownItem(BaseModel):
    """Site dropdown menu item configuration."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    title: str = Field(..., min_length=1, description="Menu item title")
    icon: str = Field(..., min_length=1, description="Material icon name")
    link: str = Field(..., min_length=1, description="Link URL")
