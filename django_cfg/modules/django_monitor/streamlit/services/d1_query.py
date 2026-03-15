"""
django_monitor.streamlit.services.d1_query — read-only D1 queries for Streamlit pages.

Works both inside Django (reads CloudflareConfig) and standalone Streamlit process
(reads credentials from CLOUDFLARE__ACCOUNT_ID / CLOUDFLARE__API_TOKEN /
CLOUDFLARE__D1_DATABASE_ID environment variables).
"""

from __future__ import annotations

import os
from typing import Any

from django_cfg.modules.django_cf.core import BaseD1Service
from django_cfg.modules.django_cf.core.client import CloudflareD1Client

from ..models import (
    CombinedStats,
    FrontendEvent,
    FrontendEventStats,
    ServerEvent,
    ServerEventStats,
)


class D1MonitorQuery(BaseD1Service):
    """Read-only D1 query service for Streamlit monitor pages."""

    def _client(self) -> CloudflareD1Client:
        """Build D1 client from Django config or env vars (Streamlit standalone mode)."""
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

    # ─────────────────────────────────────────────────────────────────────────
    # Projects
    # ─────────────────────────────────────────────────────────────────────────

    def get_projects(self) -> list[dict[str, Any]]:
        r = self._client().execute("SELECT * FROM projects ORDER BY project_name")
        return list(r.results or [])

    # ─────────────────────────────────────────────────────────────────────────
    # Server events
    # ─────────────────────────────────────────────────────────────────────────

    def get_server_events(
        self,
        *,
        is_resolved: bool = False,
        event_type: str | None = None,
        api_url: str | None = None,
        limit: int = 100,
    ) -> list[ServerEvent]:
        conditions = ["1=1"]
        if not is_resolved:
            conditions.append("is_resolved = 0")
        if event_type:
            conditions.append(f"event_type = '{event_type}'")
        if api_url:
            conditions.append(f"api_url = '{api_url}'")
        where = " AND ".join(conditions)
        sql = (
            f"SELECT * FROM server_events WHERE {where} "
            f"ORDER BY last_seen DESC LIMIT {limit}"
        )
        rows = self._client().execute(sql).results or []
        return [ServerEvent.from_dict(r) for r in rows]

    def get_server_event_stats(self, api_url: str | None = None) -> ServerEventStats:
        where = f"WHERE api_url = '{api_url}'" if api_url else ""
        r = self._client().execute(f"""
            SELECT
                SUM(CASE WHEN is_resolved = 0 THEN 1 ELSE 0 END) as open_errors,
                SUM(CASE WHEN is_resolved = 1 THEN 1 ELSE 0 END) as resolved,
                SUM(occurrence_count) as total_occurrences,
                SUM(CASE WHEN event_type = 'SLOW_QUERY' THEN 1 ELSE 0 END) as slow_queries
            FROM server_events {where}
        """)
        return ServerEventStats.from_dict((r.results or [{}])[0])

    def mark_server_event_resolved(self, fingerprint: str, api_url: str) -> None:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        self._client().execute(
            "UPDATE server_events SET is_resolved = 1, synced_at = ? "
            "WHERE fingerprint = ? AND api_url = ?",
            [now, fingerprint, api_url],
        )

    def reopen_server_event(self, fingerprint: str, api_url: str) -> None:
        self._client().execute(
            "UPDATE server_events SET is_resolved = 0 "
            "WHERE fingerprint = ? AND api_url = ?",
            [fingerprint, api_url],
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Frontend events
    # ─────────────────────────────────────────────────────────────────────────

    def get_frontend_events(
        self,
        *,
        event_type: str | None = None,
        browser: str | None = None,
        hours: int = 24,
        limit: int = 200,
    ) -> list[FrontendEvent]:
        conditions = [f"created_at >= datetime('now', '-{hours} hours')"]
        if event_type:
            conditions.append(f"event_type = '{event_type}'")
        if browser:
            conditions.append(f"browser = '{browser}'")
        where = " AND ".join(conditions)
        sql = (
            f"SELECT * FROM frontend_events WHERE {where} "
            f"ORDER BY created_at DESC LIMIT {limit}"
        )
        rows = self._client().execute(sql).results or []
        return [FrontendEvent.from_dict(r) for r in rows]

    def get_frontend_event_stats(self, hours: int = 24) -> FrontendEventStats:
        r = self._client().execute(f"""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN event_type = 'JS_ERROR' THEN 1 ELSE 0 END) as js_errors,
                SUM(CASE WHEN event_type = 'NETWORK_ERROR' THEN 1 ELSE 0 END) as network_errors,
                COUNT(DISTINCT ip_address) as unique_ips
            FROM frontend_events
            WHERE created_at >= datetime('now', '-{hours} hours')
        """)
        return FrontendEventStats.from_dict((r.results or [{}])[0])

    def get_frontend_events_timeline(self, hours: int = 24) -> list[dict[str, Any]]:
        # Adaptive grouping: ≤2h → by minute, ≤48h → by hour, else → by day
        if hours <= 2:
            fmt = "%Y-%m-%d %H:%M"
            label = "minute"
        elif hours <= 48:
            fmt = "%Y-%m-%d %H:00"
            label = "hour"
        else:
            fmt = "%Y-%m-%d"
            label = "day"
        r = self._client().execute(f"""
            SELECT
                strftime('{fmt}', created_at) as {label},
                COUNT(*) as count
            FROM frontend_events
            WHERE created_at >= datetime('now', '-{hours} hours')
            GROUP BY {label} ORDER BY {label}
        """)
        results = list(r.results or [])
        return [{"period": row.get(label, ""), "count": row.get("count", 0)} for row in results]

    def get_frontend_event_type_breakdown(self, hours: int = 24) -> list[dict[str, Any]]:
        r = self._client().execute(f"""
            SELECT event_type, COUNT(*) as count
            FROM frontend_events
            WHERE created_at >= datetime('now', '-{hours} hours')
            GROUP BY event_type ORDER BY count DESC
        """)
        return list(r.results or [])

    # ─────────────────────────────────────────────────────────────────────────
    # Overview
    # ─────────────────────────────────────────────────────────────────────────

    def get_top_server_errors(self, limit: int = 5) -> list[ServerEvent]:
        """Top unresolved errors by occurrence count."""
        r = self._client().execute(f"""
            SELECT * FROM server_events
            WHERE is_resolved = 0
            ORDER BY CAST(occurrence_count AS INTEGER) DESC
            LIMIT {limit}
        """)
        rows = r.results or []
        return [ServerEvent.from_dict(row) for row in rows]

    def get_combined_stats(self) -> CombinedStats:
        """Single-call combined stats for Overview page."""
        client = self._client()
        srv = client.execute("""
            SELECT
                SUM(CASE WHEN is_resolved = 0 THEN 1 ELSE 0 END) as open_errors,
                SUM(CASE WHEN is_resolved = 1 THEN 1 ELSE 0 END) as resolved,
                SUM(CAST(occurrence_count AS INTEGER)) as total_occurrences
            FROM server_events
        """)
        fe = client.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN event_type = 'JS_ERROR' THEN 1 ELSE 0 END) as js_errors,
                SUM(CASE WHEN event_type = 'NETWORK_ERROR' THEN 1 ELSE 0 END) as network_errors
            FROM frontend_events
            WHERE created_at >= datetime('now', '-24 hours')
        """)
        from ..models import _int  # noqa: PLC0415
        srv_row = (srv.results or [{}])[0]
        fe_row = (fe.results or [{}])[0]
        return CombinedStats(
            open_errors=_int(srv_row.get("open_errors")),
            resolved=_int(srv_row.get("resolved")),
            total_occurrences=_int(srv_row.get("total_occurrences")),
            fe_total_24h=_int(fe_row.get("total")),
            fe_js_errors_24h=_int(fe_row.get("js_errors")),
            fe_network_errors_24h=_int(fe_row.get("network_errors")),
        )


__all__ = ["D1MonitorQuery"]
