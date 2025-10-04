"""
Site Dropdown Models for Unfold Dashboard

Pydantic models for site dropdown menu items.
"""

from typing import Union, Callable
from pydantic import BaseModel, Field, ConfigDict, computed_field
from ..utils import auto_resolve_url


class SiteDropdownItem(BaseModel):
    """Site dropdown menu item configuration with automatic URL resolution."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    title: str = Field(..., min_length=1, description="Menu item title")
    icon: str = Field(..., min_length=1, description="Material icon name")
    link: str = Field(..., min_length=1, description="Link URL or URL name")

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
            "icon": self.icon,
            "title": self.title,
            "link": self.get_link_for_unfold(),
        }


