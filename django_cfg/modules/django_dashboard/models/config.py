from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from .tab import DashboardTab


class DashboardConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    tabs: List[DashboardTab] = []
    tailwind_css: Optional[str] = None
    default_tab: Optional[str] = None

    def get_default_slug(self) -> Optional[str]:
        if self.default_tab:
            return self.default_tab
        return self.tabs[0].slug if self.tabs else None

    def get_tab(self, slug: str) -> Optional[DashboardTab]:
        return next((t for t in self.tabs if t.slug == slug), None)
