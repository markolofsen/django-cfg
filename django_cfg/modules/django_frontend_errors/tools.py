"""MCP tools over the stored browser errors (read-only, bounded).

``session_id`` and ``user_agent`` are stored but never returned.
"""

from __future__ import annotations

import datetime as _dt
import json
from typing import Any, Dict

from django.db.models import Q
from django.utils import timezone

from django_cfg.modules.django_mcp.tools.base import MCPTool, tool_registry

MAX_ROWS = 50
MAX_STACK_LINES = 20
MAX_TEXT = 500
DEFAULT_DAYS = 7
MAX_DAYS = 365
EVENT_TYPES = ["JS_ERROR", "NETWORK_ERROR", "ERROR", "WARNING"]

_PLANE = (
    "This is the WEB plane: errors thrown in users' browsers, reported to /cfg/monitor/ingest/. "
    "It is not server exceptions and not agent crash telemetry."
)


def _int(arguments: Dict[str, Any], key: str, default: int, ceiling: int) -> int:
    try:
        value = int(arguments.get(key, default))
    except (TypeError, ValueError):
        value = default
    return max(1, min(value, ceiling))


def _clip(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit] + "…"


def _row(e, *, stack: bool) -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "id": e.pk,
        "fingerprint": e.fingerprint,
        "event_type": e.event_type,
        "level": e.level,
        "count": e.count,
        "first_seen": e.first_seen,
        "last_seen": e.last_seen,
        "message": _clip(e.message, MAX_TEXT),
        "url": _clip(e.url, MAX_TEXT),
        "environment": e.environment,
        "project_name": e.project_name,
        "build_id": e.build_id,
        "browser": e.browser,
        "os": e.os,
    }
    if e.http_status:
        data["http"] = {"status": e.http_status, "method": e.http_method, "url": _clip(e.http_url, MAX_TEXT)}
    if stack and e.stack_trace:
        lines = e.stack_trace.splitlines()
        data["stack_trace"] = "\n".join(lines[:MAX_STACK_LINES])
        if len(lines) > MAX_STACK_LINES:
            data["stack_omitted_lines"] = len(lines) - MAX_STACK_LINES
    return data


def _queryset(arguments: Dict[str, Any]):
    from .models import FrontendError

    days = _int(arguments, "days", DEFAULT_DAYS, MAX_DAYS)
    qs = FrontendError.objects.filter(last_seen__gte=timezone.now() - _dt.timedelta(days=days))
    for key in ("event_type", "environment", "project_name"):
        if arguments.get(key):
            qs = qs.filter(**{key: arguments[key]})
    return qs, days


def _dump(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, default=str, ensure_ascii=False)


def _empty(days: int) -> str:
    return _dump({
        "results": [],
        "count": 0,
        "note": (
            f"No browser errors seen in the last {days} day(s). {_PLANE} An empty result means either no "
            "errors or nothing reporting: check that the frontend posts to /cfg/monitor/ingest/ and that "
            "DjangoConfig.frontend_errors is enabled."
        ),
    })


class TopFrontendErrorsTool(MCPTool):
    name = "frontend_errors_top"
    read_only = True
    description = (
        "Browser (frontend) error signatures ranked by occurrences or recency. Use this FIRST for "
        "'what is breaking for users?'. One row per signature with count, first_seen, last_seen and the "
        f"latest url/message. {_PLANE} Use frontend_errors_recent for stacks and free-text search."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "days": {"type": "integer", "default": DEFAULT_DAYS, "description": f"Seen within this many days (ceiling {MAX_DAYS})."},
            "event_type": {"type": "string", "enum": EVENT_TYPES},
            "environment": {"type": "string"},
            "project_name": {"type": "string"},
            "sort": {"type": "string", "enum": ["count", "last_seen"], "default": "count"},
            "limit": {"type": "integer", "default": 20, "description": f"Ceiling {MAX_ROWS}."},
        },
    }

    def execute(self, context: Any, arguments: Dict[str, Any]) -> str:
        qs, days = _queryset(arguments)
        order = "-last_seen" if arguments.get("sort") == "last_seen" else "-count"
        rows = [_row(e, stack=False) for e in qs.order_by(order, "-last_seen")[: _int(arguments, "limit", 20, MAX_ROWS)]]
        if not rows:
            return _empty(days)
        return _dump({"results": rows, "count": len(rows), "window_days": days, "sorted_by": order})


class RecentFrontendErrorsTool(MCPTool):
    name = "frontend_errors_recent"
    read_only = True
    description = (
        "Browser (frontend) errors, newest first, with a truncated stack. Filter by `fingerprint` to read "
        "one signature, or by `query` (case-insensitive over message and URL). "
        f"{_PLANE} Never returns session ids or user agents."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "fingerprint": {"type": "string"},
            "days": {"type": "integer", "default": DEFAULT_DAYS},
            "event_type": {"type": "string", "enum": EVENT_TYPES},
            "environment": {"type": "string"},
            "project_name": {"type": "string"},
            "limit": {"type": "integer", "default": 20, "description": f"Ceiling {MAX_ROWS}."},
        },
    }

    def execute(self, context: Any, arguments: Dict[str, Any]) -> str:
        qs, days = _queryset(arguments)
        if arguments.get("query"):
            q = str(arguments["query"]).strip()
            qs = qs.filter(Q(message__icontains=q) | Q(url__icontains=q))
        if arguments.get("fingerprint"):
            qs = qs.filter(fingerprint=arguments["fingerprint"])
        limit = _int(arguments, "limit", 20, MAX_ROWS)
        found = list(qs.order_by("-last_seen")[: limit + 1])
        rows = [_row(e, stack=True) for e in found[:limit]]
        if not rows:
            return _empty(days)
        payload = {"results": rows, "count": len(rows), "has_more": len(found) > limit, "window_days": days}
        return _dump(payload)


def register() -> None:
    for tool in (TopFrontendErrorsTool(), RecentFrontendErrorsTool()):
        tool_registry.register(tool)
