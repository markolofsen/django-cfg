"""Pydantic models for D1 log event data."""

from __future__ import annotations

from pydantic import BaseModel


class LogEventSyncData(BaseModel):
    """One row in the log_events D1 table."""

    fingerprint: str
    api_url: str
    level: str
    logger_name: str
    message: str
    module: str = ""
    func_name: str = ""
    pathname: str = ""
    lineno: int = 0
    stack_trace: str = ""
    extra: str = "{}"
    occurrence_count: int = 1
    is_resolved: int = 0
    first_seen: str = ""
    last_seen: str = ""


__all__ = ["LogEventSyncData"]
