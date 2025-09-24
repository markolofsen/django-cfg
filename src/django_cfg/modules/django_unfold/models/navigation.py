"""
Navigation Models for Unfold Dashboard

Pydantic models for navigation items and sections.
"""

from typing import List, Optional, Union, Callable
from pydantic import BaseModel, Field, ConfigDict, computed_field
from enum import Enum
from ..utils import auto_resolve_url


class NavigationItemType(str, Enum):
    """Navigation item types."""
    LINK = "link"
    SEPARATOR = "separator"
    GROUP = "group"


class NavigationItem(BaseModel):
    """Single navigation item configuration with automatic URL resolution."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    title: str = Field(..., min_length=1, description="Navigation item title")
    icon: Optional[str] = Field(None, description="Material icon name")
    link: Optional[str] = Field(None, description="URL link or URL name")
    badge: Optional[str] = Field(None, description="Badge callback function path")
    permission: Optional[str] = Field(None, description="Permission callback function path")
    type: NavigationItemType = Field(default=NavigationItemType.LINK, description="Item type")

    @computed_field
    @property
    def resolved_link(self) -> Union[str, Callable]:
        """Get the link resolved for Unfold (computed field to avoid recursion)."""
        if self.link:
            return auto_resolve_url(self.link)
        return "#"

    def get_link_for_unfold(self):
        """Get the link in the format expected by Unfold."""
        return self.resolved_link
    
    def to_dict(self) -> dict:
        """Convert to dictionary for Unfold admin."""
        return {
            "title": self.title,
            "icon": self.icon,
            "link": self.get_link_for_unfold(),
            "badge": self.badge,
            "permission": self.permission,
        }



class NavigationSection(BaseModel):
    """Navigation section configuration."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    title: str = Field(..., min_length=1, description="Section title")
    separator: bool = Field(default=True, description="Show separator")
    collapsible: bool = Field(default=True, description="Section is collapsible")
    items: List[NavigationItem] = Field(default_factory=list, description="Navigation items")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for Unfold admin."""
        return {
            "title": self.title,
            "separator": self.separator,
            "collapsible": self.collapsible,
            "items": [item.to_dict() for item in self.items],
        }


