from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator


class DashboardTab(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    slug: str
    title: str
    icon: str = "dashboard"
    template: Optional[str] = None
    callback: Optional[str] = None
    permission: Optional[str] = None
    superuser_only: bool = False

    @model_validator(mode="after")
    def requires_template_or_callback(self) -> "DashboardTab":
        if not self.template and not self.callback:
            raise ValueError(f"DashboardTab '{self.slug}' requires at least one of: template, callback")
        return self
