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
    brand: str = ""  # which site/product the lead came from (multi_select); "" = not written
    received_at: Optional[datetime] = None
    source: str = "Website"  # Website, Telegram, Referral, Other, Email
    extra: Dict[str, Any] = Field(default_factory=dict)
