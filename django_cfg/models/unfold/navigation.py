"""
Navigation Models for Unfold Dashboard

Pydantic models for navigation items and sections.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class NavigationItemType(str, Enum):
    """Navigation item types."""
    LINK = "link"
    SEPARATOR = "separator"
    GROUP = "group"


class NavigationItem(BaseModel):
    """Single navigation item configuration."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    title: str = Field(..., min_length=1, description="Navigation item title")
    icon: Optional[str] = Field(None, description="Material icon name")
    link: Optional[str] = Field(None, description="URL link")
    badge: Optional[str] = Field(None, description="Badge callback function path")
    permission: Optional[str] = Field(None, description="Permission callback function path")
    type: NavigationItemType = Field(default=NavigationItemType.LINK, description="Item type")


class NavigationSection(BaseModel):
    """Navigation section configuration."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    title: str = Field(..., min_length=1, description="Section title")
    separator: bool = Field(default=True, description="Show separator")
    collapsible: bool = Field(default=True, description="Section is collapsible")
    items: List[NavigationItem] = Field(default_factory=list, description="Navigation items")
