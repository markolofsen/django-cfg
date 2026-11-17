"""NotionLead -> the ``properties`` dict of ``pages.create``."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, List
from urllib.parse import urlsplit

from .__cfg__ import NotionTarget
from .details import build_details, humanize
from .lead import NotionLead

CHUNK = 2000
MAX_MESSAGE = 10000
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
SOURCES = {"website", "telegram", "referral", "other", "email"}


def rich_text(text: str, limit: int = CHUNK) -> List[Dict[str, Any]]:
    """Notion rich_text value: chunks of <= 2000 characters (the per-item limit); ``limit`` caps the total."""
    text = text[:limit]
    return [{"type": "text", "text": {"content": text[i : i + CHUNK]}} for i in range(0, len(text), CHUNK)]


def _iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def _valid_url(value: str) -> bool:
    parts = urlsplit(value)
    return parts.scheme in ("http", "https") and bool(parts.netloc) and len(value) <= 2000


def build_properties(lead: NotionLead, target: NotionTarget, key: str, *, source_default: str = "Website") -> Dict[str, Any]:
    return _build(lead, target, key, source_default)[0]


def _build(lead: NotionLead, target: NotionTarget, key: str, source_default: str = "Website"):
    """(properties, details text). Properties for ``pages.create``. Empty values are omitted; a value its column cannot hold, or a column the target
    disabled, goes to Details instead so nothing is lost."""
    extra = dict(lead.extra)
    props: Dict[str, Any] = {}

    def put(logical: str, builder) -> bool:
        column = target.column(logical)
        if column is None:
            return False
        props[column] = builder()
        return True

    def text_field(logical: str, value: str, limit: int = CHUNK) -> None:
        if not value:
            return
        if not put(logical, lambda: {"rich_text": rich_text(value, limit)}):
            extra[humanize(logical)] = value

    title = lead.name or lead.company or lead.email or lead.phone or "Lead"
    put("name", lambda: {"title": rich_text(title)})
    put("status", lambda: {"select": {"name": "New"}})
    source = lead.source if lead.source.lower() in SOURCES else source_default
    put("source", lambda: {"select": {"name": source[:1].upper() + source[1:].lower()}})

    if lead.email:
        if not (_EMAIL.match(lead.email.strip()) and put("email", lambda: {"email": lead.email.strip()})):
            extra["Email"] = lead.email
    if lead.phone and not put("phone", lambda: {"phone_number": lead.phone.strip()[:200]}):
        extra["Phone"] = lead.phone
    if lead.page_url:
        if _valid_url(lead.page_url.strip()):
            if not put("page_url", lambda: {"url": lead.page_url.strip()}):
                extra["Page URL"] = lead.page_url
        else:
            extra["Page URL"] = lead.page_url

    text_field("message", lead.message, MAX_MESSAGE)
    text_field("form", lead.form)
    if lead.brand:
        brand = lead.brand.replace(",", " ").strip()[:100]
        if not put("brand", lambda: {"multi_select": [{"name": brand}]}):
            extra["Brand"] = lead.brand
    if lead.received_at:
        put("received_at", lambda: {"date": {"start": _iso(lead.received_at)}})

    details = build_details(extra)
    if details:
        if target.column("details") is not None:
            put("details", lambda: {"rich_text": rich_text(details, 8000)})
    put("run_id", lambda: {"rich_text": rich_text(key)})
    return props, details


def details_children(lead: NotionLead, target: NotionTarget) -> List[Dict[str, Any]]:
    """Page body with the Details text, used only when the target has no Details column (so the lead is never lost)."""
    if target.column("details") is not None:
        return []
    details = _build(lead, target, "")[1]
    if not details:
        return []
    return [{"object": "block", "type": "paragraph", "paragraph": {"rich_text": rich_text(details, 8000)}}]
