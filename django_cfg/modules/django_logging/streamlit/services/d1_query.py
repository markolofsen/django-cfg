"""D1 read-only query service for Logging Streamlit pages."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from django_cfg.modules.django_cf.core import BaseD1Service, CloudflareD1Client, D1Q

from ...core.schema import LOG_EVENTS_TABLE


@dataclass
class LogEventStats:
    """Aggregate stats for log events."""

    open_errors: int = 0
    open_warnings: int = 0
    resolved: int = 0
    total_occurrences: int = 0

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> "LogEventStats":
        return cls(
            open_errors=int(row.get("open_errors") or 0),
            open_warnings=int(row.get("open_warnings") or 0),
            resolved=int(row.get("resolved") or 0),
            total_occurrences=int(row.get("total_occurrences") or 0),
        )


class D1LoggingQuery(BaseD1Service):
    """Read-only D1 query service for Streamlit logging pages."""

    def _get_schema_statements(self) -> list[str]:
        return []  # read-only — never create tables

    def _client(self) -> CloudflareD1Client:
        """Build D1 client from Django config or env vars (standalone Streamlit)."""
        try:
            return self._get_client()
        except Exception:
            pass

        account_id = os.environ.get("CLOUDFLARE__ACCOUNT_ID", "")
        api_token = os.environ.get("CLOUDFLARE__API_TOKEN", "")
        database_id = os.environ.get("CLOUDFLARE__D1_DATABASE_ID", "")
        if not (account_id and api_token and database_id):
            raise RuntimeError(
                "Cloudflare D1 credentials not found. "
                "Set CLOUDFLARE__ACCOUNT_ID, CLOUDFLARE__API_TOKEN, CLOUDFLARE__D1_DATABASE_ID."
            )
        return CloudflareD1Client(
            account_id=account_id,
            api_token=api_token,
            database_id=database_id,
        )

    def get_projects(self) -> list[dict[str, Any]]:
        """Get all projects from the projects table."""
        sql, params = D1Q.select(
            "projects",
            order_by="synced_at DESC",
        )
        return self._client().execute(sql, params).results or []

    def get_log_events(
        self,
        *,
        is_resolved: bool = False,
        level: str | None = None,
        api_url: str | None = None,
        search: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Query log events with optional filters."""
        parts: list[str] = []
        sql_params: list[str] = []

        if not is_resolved:
            parts.append("is_resolved = 0")
        if level:
            parts.append("level = ?")
            sql_params.append(level)
        if api_url:
            parts.append("api_url = ?")
            sql_params.append(api_url)
        if search:
            parts.append("(message LIKE ? OR stack_trace LIKE ? OR logger_name LIKE ?)")
            sql_params.extend([f"%{search}%"] * 3)

        where = " AND ".join(parts) if parts else None
        sql, params = D1Q.select_raw(
            LOG_EVENTS_TABLE,
            where_clause=where,
            params=sql_params or None,
            order_by="last_seen DESC",
            limit=limit,
        )
        return self._client().execute(sql, params).results or []

    def get_log_event_stats(self, api_url: str | None = None) -> LogEventStats:
        """Aggregate stats for log events."""
        sql, params = D1Q.aggregate(
            LOG_EVENTS_TABLE,
            expressions=[
                "SUM(CASE WHEN is_resolved = 0 AND level = 'error' THEN 1 ELSE 0 END) as open_errors",
                "SUM(CASE WHEN is_resolved = 0 AND level = 'warning' THEN 1 ELSE 0 END) as open_warnings",
                "SUM(CASE WHEN is_resolved = 1 THEN 1 ELSE 0 END) as resolved",
                "SUM(occurrence_count) as total_occurrences",
            ],
            where_clause="api_url = ?" if api_url else None,
            params=[api_url] if api_url else None,
        )
        r = self._client().execute(sql, params)
        return LogEventStats.from_dict((r.results or [{}])[0])

    def mark_resolved(self, fingerprint: str, api_url: str) -> None:
        """Mark a log event as resolved."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc).isoformat()
        self._client().execute(
            "UPDATE log_events SET is_resolved = 1, last_seen = ? "
            "WHERE fingerprint = ? AND api_url = ?",
            [now, fingerprint, api_url],
        )

    def reopen_event(self, fingerprint: str, api_url: str) -> None:
        """Reopen a resolved log event."""
        self._client().execute(
            "UPDATE log_events SET is_resolved = 0 "
            "WHERE fingerprint = ? AND api_url = ?",
            [fingerprint, api_url],
        )
