"""
django_monitor.streamlit.models — typed dataclasses for D1 monitor data.

Normalises D1 quirks at the boundary (str→int, "0"/"1"→bool, None→"")
so page code never has to deal with raw JSON artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


def _int(v: Any, default: int = 0) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _bool_flag(v: Any) -> bool:
    """D1 returns is_resolved as integer 0/1 or string '0'/'1'."""
    return str(v) == "1"


def _str(v: Any) -> str:
    if v is None:
        return ""
    return str(v)


@dataclass(slots=True)
class ServerEvent:
    fingerprint: str
    event_type: str
    level: str
    message: str
    module: str
    func_name: str
    url: str
    http_method: str
    stack_trace: str
    extra: str
    api_url: str
    occurrence_count: int
    is_resolved: bool
    first_seen: str
    last_seen: str

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> "ServerEvent":
        return cls(
            fingerprint=_str(row.get("fingerprint")),
            event_type=_str(row.get("event_type")),
            level=_str(row.get("level")),
            message=_str(row.get("message")),
            module=_str(row.get("module")),
            func_name=_str(row.get("func_name")),
            url=_str(row.get("url")),
            http_method=_str(row.get("http_method")),
            stack_trace=_str(row.get("stack_trace")),
            extra=_str(row.get("extra", "{}")),
            api_url=_str(row.get("api_url")),
            occurrence_count=_int(row.get("occurrence_count")),
            is_resolved=_bool_flag(row.get("is_resolved", 0)),
            first_seen=_str(row.get("first_seen")),
            last_seen=_str(row.get("last_seen")),
        )

    def to_display_dict(self) -> dict[str, Any]:
        """Flat dict for AgGrid / DataFrame — no raw D1 types."""
        return {
            "fingerprint": self.fingerprint,
            "status": "✅ resolved" if self.is_resolved else "🔴 open",
            "event_type": self.event_type,
            "level": self.level,
            "message": self.message,
            "module": self.module,
            "count": self.occurrence_count,
            "last_seen": self.last_seen,
        }


@dataclass(slots=True)
class FrontendEvent:
    id: str
    event_type: str
    level: str
    message: str
    stack_trace: str
    url: str
    http_method: str
    http_status: int
    http_url: str
    browser: str
    os: str
    device_type: str
    user_agent: str
    ip_address: str
    environment: str
    build_id: str
    extra: str
    last_seen: str

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> "FrontendEvent":
        return cls(
            id=_str(row.get("id")),
            event_type=_str(row.get("event_type")),
            level=_str(row.get("level")),
            message=_str(row.get("message")),
            stack_trace=_str(row.get("stack_trace")),
            url=_str(row.get("url")),
            http_method=_str(row.get("http_method")),
            http_status=_int(row.get("http_status")),
            http_url=_str(row.get("http_url")),
            browser=_str(row.get("browser")),
            os=_str(row.get("os")),
            device_type=_str(row.get("device_type")),
            user_agent=_str(row.get("user_agent")),
            ip_address=_str(row.get("ip_address")),
            environment=_str(row.get("environment")),
            build_id=_str(row.get("build_id")),
            extra=_str(row.get("extra", "{}")),
            last_seen=_str(row.get("last_seen")),
        )

    def to_display_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "event_type": self.event_type,
            "level": self.level,
            "message": self.message[:120],
            "browser": self.browser,
            "os": self.os,
            "device_type": self.device_type,
            "ip_address": self.ip_address,
            "url": self.url,
            "last_seen": self.last_seen,
        }


@dataclass(slots=True)
class ServerEventStats:
    open_errors: int
    resolved: int
    total_occurrences: int
    slow_queries: int

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> "ServerEventStats":
        return cls(
            open_errors=_int(row.get("open_errors")),
            resolved=_int(row.get("resolved")),
            total_occurrences=_int(row.get("total_occurrences")),
            slow_queries=_int(row.get("slow_queries")),
        )


@dataclass(slots=True)
class FrontendEventStats:
    total: int
    js_errors: int
    network_errors: int
    unique_ips: int

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> "FrontendEventStats":
        return cls(
            total=_int(row.get("total")),
            js_errors=_int(row.get("js_errors")),
            network_errors=_int(row.get("network_errors")),
            unique_ips=_int(row.get("unique_ips")),
        )


@dataclass(slots=True)
class CombinedStats:
    open_errors: int
    resolved: int
    total_occurrences: int
    fe_total_24h: int
    fe_js_errors_24h: int
    fe_network_errors_24h: int


@dataclass(slots=True)
class D1User:
    id: str
    api_url: str
    email: str
    first_name: str
    last_name: str
    phone: str
    company: str
    position: str
    is_active: bool
    date_joined: str
    updated_at: str
    synced_at: str

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> "D1User":
        return cls(
            id=_str(row.get("id")),
            api_url=_str(row.get("api_url")),
            email=_str(row.get("email")),
            first_name=_str(row.get("first_name")),
            last_name=_str(row.get("last_name")),
            phone=_str(row.get("phone")),
            company=_str(row.get("company")),
            position=_str(row.get("position")),
            is_active=_bool_flag(row.get("is_active", 1)),
            date_joined=_str(row.get("date_joined")),
            updated_at=_str(row.get("updated_at")),
            synced_at=_str(row.get("synced_at")),
        )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def to_display_dict(self) -> dict[str, Any]:
        return {
            "status": "✅ active" if self.is_active else "⛔ inactive",
            "email": self.email,
            "name": self.full_name,
            "company": self.company,
            "position": self.position,
            "phone": self.phone,
            "date_joined": self.date_joined[:10] if self.date_joined else "",
            "synced_at": self.synced_at[:16] if self.synced_at else "",
        }


@dataclass(slots=True)
class D1UserStats:
    total: int
    active: int
    inactive: int
    projects: int

    @classmethod
    def from_rows(cls, stats_row: dict[str, Any], projects_count: int) -> "D1UserStats":
        return cls(
            total=_int(stats_row.get("total")),
            active=_int(stats_row.get("active")),
            inactive=_int(stats_row.get("inactive")),
            projects=projects_count,
        )


__all__ = [
    "ServerEvent",
    "FrontendEvent",
    "ServerEventStats",
    "FrontendEventStats",
    "CombinedStats",
    "D1User",
    "D1UserStats",
]
