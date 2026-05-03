"""
Navigation Models for Unfold Dashboard

Pydantic models for navigation items and sections.
"""

import logging
import re
from enum import Enum
from typing import Callable, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, computed_field

from ..utils import auto_resolve_url

logger = logging.getLogger(__name__)


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
    permission: Optional[Union[str, Callable]] = Field(None, description="Permission callback function or import path")
    type: NavigationItemType = Field(default=NavigationItemType.LINK, description="Item type")

    @computed_field
    @property
    def resolved_link(self) -> Union[str, Callable]:
        """Get the link resolved for Unfold."""
        if self.link:
            return auto_resolve_url(self.link)
        return "#"

    def get_link_for_unfold(self):
        """Get the link in the format expected by Unfold."""
        return self.resolved_link

    def to_dict(self) -> dict:
        """Convert to dictionary for Unfold admin."""
        from django.urls import reverse_lazy, NoReverseMatch
        link = self.link
        if link and not link.startswith(("/", "http")):
            try:
                link = str(reverse_lazy(link))
            except NoReverseMatch:
                pass

        permission = self.permission
        if not permission and self.link and self.link.startswith("admin:"):
            permission = self._auto_permission_callback(self.link)

        return {
            "title": self.title,
            "icon": self.icon,
            "link": link,
            "badge": self.badge,
            "permission": permission,
        }

    @staticmethod
    def _auto_permission_callback(link: str):
        """Build a permission callable from an admin changelist URL name."""
        match = re.match(r"^admin:(?P<app>[a-z_]+)_(?P<model>[a-z]+)_changelist$", link)
        if not match:
            return None
        app_label = match.group("app")
        model = match.group("model")

        def _checker(request) -> bool:
            if not request.user or not request.user.is_authenticated:
                return False
            if request.user.is_superuser:
                return True
            return request.user.has_perm(f"{app_label}.view_{model}")

        return _checker



class NavigationSection(BaseModel):
    """Navigation section configuration."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    title: str = Field(..., min_length=1, description="Section title")
    separator: bool = Field(default=True, description="Show separator")
    collapsible: bool = Field(default=True, description="Section is collapsible")
    open: bool = Field(default=False, description="Section is open by default")
    items: List[NavigationItem] = Field(default_factory=list, description="Navigation items")

    def to_dict(self) -> dict:
        """Convert to dictionary for Unfold admin."""
        result = {
            "title": self.title,
            "separator": self.separator,
            "collapsible": self.collapsible,
            "items": [item.to_dict() for item in self.items],
        }
        # Add open only if True (to avoid breaking existing navigation)
        if self.open:
            result["open"] = True
        return result


