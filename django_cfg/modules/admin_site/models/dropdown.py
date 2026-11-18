"""
Header links of the admin site (``AdminSiteConfig.site_dropdown``).
"""

from typing import Callable, Union

from pydantic import BaseModel, ConfigDict, Field, computed_field

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
        """The link, with URL names turned into resolvers (computed field to avoid recursion)."""
        if self.link:
            return auto_resolve_url(self.link)
        return "#"

    def to_dict(self) -> dict:
        """The dict ``CfgAdminSite`` reads from ``SITE_DROPDOWN``."""
        return {
            "icon": self.icon,
            "title": self.title,
            "link": self.resolved_link,
        }


