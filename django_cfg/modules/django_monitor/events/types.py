"""
django_monitor.events.types — Pydantic v2 types for D1 sync.

Field names match D1 column names exactly so D1Q._extract() pulls
values directly from model_dump() — no manual to_params() methods.

ServerEventSyncData  — upsert_increment by (fingerprint, api_url)
FrontendEventSyncData — INSERT OR IGNORE by (id, api_url)
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from django_cfg.modules.django_monitor.utils import parse_user_agent


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─────────────────────────────────────────────────────────────────────────────
# Server events
# ─────────────────────────────────────────────────────────────────────────────

class ServerEventSyncData(BaseModel):
    """Typed model for ServerEvent → D1 upsert_increment.

    All fields match SERVER_EVENTS_TABLE column names.
    occurrence_count / is_resolved are included so D1Q._extract()
    can build the full INSERT param list; on conflict the DB
    handles incrementing / resetting them.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    fingerprint: str = Field(..., description="sha256[:16] of exc_type::module::func_name")
    api_url:     str = Field(..., description="Project API URL — composite PK")

    event_type: str = Field(..., description="SERVER_ERROR|SLOW_QUERY|RQ_FAILURE|LOG_ERROR|UNHANDLED_EXCEPTION")
    level:      str = Field(..., description="error | warning | info | debug")

    message:     str = ""
    stack_trace: str = ""
    logger_name: str = ""

    url:         str = ""
    http_method: str = ""
    http_status: Optional[str] = None   # stored as TEXT-compatible string or ""

    func_name: str = ""
    module:    str = ""
    lineno:    Optional[str] = None     # stored as TEXT-compatible string or ""

    extra: str = "{}"                   # JSON string — serialised before storing

    occurrence_count: str = "1"         # initial value; DB increments on conflict
    is_resolved:      str = "0"         # reset to 0 on every new occurrence

    first_seen: str = Field(default_factory=_now_iso)
    last_seen:  str = Field(default_factory=_now_iso)
    synced_at:  str = Field(default_factory=_now_iso)

    @classmethod
    def from_event(cls, event: Any, api_url: str) -> "ServerEventSyncData":
        """Build from a duck-typed event object (capture modules produce these)."""
        now = _now_iso()
        extra_raw = getattr(event, "extra", {}) or {}
        if not isinstance(extra_raw, str):
            extra_raw = json.dumps(dict(extra_raw), ensure_ascii=False)[:5000]

        http_status = getattr(event, "http_status", None)
        lineno = getattr(event, "lineno", None)

        return cls(
            fingerprint=event.fingerprint,
            api_url=api_url.rstrip("/"),
            event_type=event.event_type,
            level=event.level,
            message=(event.message or "")[:2000],
            stack_trace=(event.stack_trace or "")[:10000],
            logger_name=(getattr(event, "logger_name", "") or "")[:200],
            url=(event.url or "")[:2000],
            http_method=(event.http_method or "")[:10],
            http_status=str(http_status) if http_status is not None else "",
            func_name=(event.func_name or "")[:200],
            module=(event.module or "")[:300],
            lineno=str(lineno) if lineno is not None else "",
            extra=extra_raw,
            first_seen=event.first_seen.isoformat() if getattr(event, "first_seen", None) else now,
            last_seen=event.last_seen.isoformat() if getattr(event, "last_seen", None) else now,
            synced_at=now,
        )

    # keep backward compat for existing MonitorSyncService call
    @classmethod
    def from_django_model(cls, event: Any, api_url: str) -> "ServerEventSyncData":
        return cls.from_event(event, api_url)


# ─────────────────────────────────────────────────────────────────────────────
# Frontend events
# ─────────────────────────────────────────────────────────────────────────────

class FrontendEventSyncData(BaseModel):
    """Typed model for FrontendEvent → D1 INSERT OR IGNORE.

    All fields match FRONTEND_EVENTS_TABLE column names.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    id:      str = Field(default_factory=lambda: str(uuid.uuid4()))
    api_url: str = Field(..., description="Project API URL — composite PK")

    event_type: str = Field(..., description="JS_ERROR|NETWORK_ERROR|ERROR|WARNING|PAGE_VIEW|PERFORMANCE|CONSOLE")
    level: str

    message:     str = ""
    stack_trace: str = ""
    url:         str = ""

    http_status: Optional[str] = None
    http_method: str = ""
    http_url:    str = ""

    user_agent:  str = ""
    ip_address:  str = ""
    device_type: str = ""
    os:          str = ""
    browser:     str = ""

    fingerprint: str = ""
    user_id:     Optional[str] = None

    extra:       str = "{}"         # JSON string
    build_id:    str = ""
    environment: str = ""

    created_at: str = Field(default_factory=_now_iso)

    @classmethod
    def from_ingest(
        cls,
        ev: dict,
        api_url: str,
        ip_address: str,
        user_id: Optional[str] = None,
    ) -> "FrontendEventSyncData":
        """Build from a validated ingest payload dict (from IngestBatchSerializer)."""
        extra_raw = ev.get("extra") or {}
        if not isinstance(extra_raw, str):
            extra_raw = json.dumps(extra_raw, ensure_ascii=False)[:3000]

        http_status = ev.get("http_status")
        ua = (ev.get("user_agent") or "")[:500]
        browser, os_name, device_type = parse_user_agent(ua)

        return cls(
            api_url=api_url.rstrip("/"),
            event_type=ev["event_type"],
            level=ev.get("level", "error"),
            message=(ev.get("message") or "")[:5000],
            stack_trace=(ev.get("stack_trace") or "")[:10000],
            url=(ev.get("url") or "")[:2000],
            http_status=str(http_status) if http_status is not None else "",
            http_method=(ev.get("http_method") or "")[:10],
            http_url=(ev.get("http_url") or "")[:2000],
            user_agent=ua,
            ip_address=ip_address,
            browser=browser,
            os=os_name,
            device_type=device_type,
            fingerprint=(ev.get("fingerprint") or "")[:64],
            user_id=user_id,
            extra=extra_raw,
            build_id=(ev.get("build_id") or "")[:100],
            environment=(ev.get("environment") or "")[:20],
        )

    @classmethod
    def from_django_model(cls, event: Any, api_url: str) -> "FrontendEventSyncData":
        """Build from Django FrontendEvent ORM instance."""
        extra_raw = getattr(event, "extra", {}) or {}
        if not isinstance(extra_raw, str):
            extra_raw = json.dumps(dict(extra_raw), ensure_ascii=False)[:3000]

        http_status = getattr(event, "http_status", None)
        user_id: Optional[str] = None
        if event.user_id:
            user_id = str(event.user_id)

        return cls(
            id=str(event.pk),
            api_url=api_url.rstrip("/"),
            event_type=event.event_type,
            level=event.level,
            message=(event.message or "")[:5000],
            stack_trace=(event.stack_trace or "")[:10000],
            url=(event.url or "")[:2000],
            http_status=str(http_status) if http_status is not None else "",
            http_method=(event.http_method or "")[:10],
            http_url=(event.http_url or "")[:2000],
            user_agent=(event.user_agent or "")[:500],
            ip_address=str(event.ip_address or ""),
            device_type=(event.device_type or "")[:10],
            os=(event.os or "")[:50],
            browser=(event.browser or "")[:50],
            fingerprint=(event.fingerprint or "")[:64],
            user_id=user_id,
            extra=extra_raw,
            build_id=(event.build_id or "")[:100],
            environment=(event.environment or "")[:20],
            created_at=event.created_at.isoformat() if event.created_at else _now_iso(),
        )


__all__ = [
    "ServerEventSyncData",
    "FrontendEventSyncData",
]
