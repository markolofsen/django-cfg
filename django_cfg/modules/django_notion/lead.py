"""The standard lead an adapter produces."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class NotionLead(BaseModel):
    """One lead in the schema of the Notion "Leads" database. Only what people filter or sort by has a column; ``extra`` holds everything else (UTM, ad clicks, locale, company, ...) and lands in Details."""

    model_config = ConfigDict(extra="forbid")

    name: str = ""
    email: str = ""
    phone: str = ""
    message: str = ""
    form: str = ""
    page_url: str = ""
    brand: str = ""  # an explicit Brand option; "" = the option matching ``project`` (keys.brand_option)
    site: str = ""  # django-cfg site key, when the adapter knows it better than the request (a declared site field)
    project: str = ""  # project key; "" = NotionConfig.project_keys[site], filled by enrich
    received_at: Optional[datetime] = None
    source: str = "Website"  # Website, Telegram, Referral, Other, Email
    extra: Dict[str, Any] = Field(default_factory=dict)
