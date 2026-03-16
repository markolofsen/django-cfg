"""
django_monitor.streamlit.services.d1_query — read-only D1 queries for Streamlit pages.

Works both inside Django (reads CloudflareConfig) and standalone Streamlit process
(reads credentials from CLOUDFLARE__ACCOUNT_ID / CLOUDFLARE__API_TOKEN /
CLOUDFLARE__D1_DATABASE_ID environment variables).

All SELECT queries use D1Q typed methods — no raw SQL strings in service layer.
"""

from __future__ import annotations

import os
from typing import Any

from django_cfg.modules.django_cf.core import BaseD1Service
from django_cfg.modules.django_cf.core.client import CloudflareD1Client
from django_cfg.modules.django_cf.core.d1_query import D1Q
from django_cfg.modules.django_cf.users.schema import PROJECTS_TABLE, USERS_TABLE
from django_cfg.modules.django_monitor.events.schema import (
    FRONTEND_EVENTS_TABLE,
    SERVER_EVENTS_TABLE,
)

from ..models import (
    CombinedStats,
    D1User,
    D1UserStats,
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
        sql, params = D1Q.select(PROJECTS_TABLE, order_by="project_name")
        r = self._client().execute(sql, params)
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
        conditions: dict[str, Any] = {}
        if not is_resolved:
            conditions["is_resolved"] = "0"
        if api_url:
            conditions["api_url"] = api_url
        if event_type:
            conditions["event_type"] = event_type

        sql, params = D1Q.select(
            SERVER_EVENTS_TABLE,
            conditions=conditions or None,
            order_by="last_seen DESC",
            limit=limit,
        )
        rows = self._client().execute(sql, params).results or []
        return [ServerEvent.from_dict(r) for r in rows]

    def get_server_event_stats(self, api_url: str | None = None) -> ServerEventStats:
        sql, params = D1Q.aggregate(
            SERVER_EVENTS_TABLE,
            expressions=[
                "SUM(CASE WHEN is_resolved = 0 THEN 1 ELSE 0 END) as open_errors",
                "SUM(CASE WHEN is_resolved = 1 THEN 1 ELSE 0 END) as resolved",
                "SUM(occurrence_count) as total_occurrences",
                "SUM(CASE WHEN event_type = 'SLOW_QUERY' THEN 1 ELSE 0 END) as slow_queries",
            ],
            where_clause="api_url = ?" if api_url else None,
            params=[api_url] if api_url else None,
        )
        r = self._client().execute(sql, params)
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
        extra_conditions: list[str] = []
        params: list[str] = [f"-{hours}"]

        if event_type:
            extra_conditions.append(f"event_type = '{event_type}'")
        if browser:
            extra_conditions.append(f"browser = '{browser}'")

        where_parts = [f"last_seen >= datetime('now', ? || ' hours')"]
        where_parts.extend(extra_conditions)
        where_clause = " AND ".join(where_parts)

        sql, safe_params = D1Q.select_raw(
            FRONTEND_EVENTS_TABLE,
            where_clause=where_clause,
            params=params,
            order_by="last_seen DESC",
            limit=limit,
        )
        rows = self._client().execute(sql, safe_params).results or []
        return [FrontendEvent.from_dict(r) for r in rows]

    def get_frontend_event_stats(self, hours: int = 24) -> FrontendEventStats:
        sql, params = D1Q.aggregate(
            FRONTEND_EVENTS_TABLE,
            expressions=[
                "COUNT(*) as total",
                "SUM(CASE WHEN event_type = 'JS_ERROR' THEN 1 ELSE 0 END) as js_errors",
                "SUM(CASE WHEN event_type = 'NETWORK_ERROR' THEN 1 ELSE 0 END) as network_errors",
                "COUNT(DISTINCT ip_address) as unique_ips",
            ],
            where_clause="last_seen >= datetime('now', ? || ' hours')",
            params=[f"-{hours}"],
        )
        r = self._client().execute(sql, params)
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

        sql, params = D1Q.group_by(
            FRONTEND_EVENTS_TABLE,
            select_expr=f"strftime('{fmt}', last_seen) as {label}, COUNT(*) as count",
            group_by=label,
            where_clause="last_seen >= datetime('now', ? || ' hours')",
            params=[f"-{hours}"],
            order_by=label,
        )
        results = list(self._client().execute(sql, params).results or [])
        return [{"period": row.get(label, ""), "count": row.get("count", 0)} for row in results]

    def get_frontend_event_type_breakdown(self, hours: int = 24) -> list[dict[str, Any]]:
        sql, params = D1Q.group_by(
            FRONTEND_EVENTS_TABLE,
            select_expr="event_type, COUNT(*) as count",
            group_by="event_type",
            where_clause="last_seen >= datetime('now', ? || ' hours')",
            params=[f"-{hours}"],
            order_by="count DESC",
        )
        return list(self._client().execute(sql, params).results or [])

    # ─────────────────────────────────────────────────────────────────────────
    # Overview
    # ─────────────────────────────────────────────────────────────────────────

    def get_top_server_errors(self, limit: int = 5) -> list[ServerEvent]:
        """Top unresolved errors by occurrence count."""
        sql, params = D1Q.select(
            SERVER_EVENTS_TABLE,
            conditions={"is_resolved": "0"},
            order_by="CAST(occurrence_count AS INTEGER) DESC",
            limit=limit,
        )
        rows = self._client().execute(sql, params).results or []
        return [ServerEvent.from_dict(row) for row in rows]

    def get_combined_stats(self) -> CombinedStats:
        """Single-call combined stats for Overview page."""
        client = self._client()

        srv_sql, srv_params = D1Q.aggregate(
            SERVER_EVENTS_TABLE,
            expressions=[
                "SUM(CASE WHEN is_resolved = 0 THEN 1 ELSE 0 END) as open_errors",
                "SUM(CASE WHEN is_resolved = 1 THEN 1 ELSE 0 END) as resolved",
                "SUM(CAST(occurrence_count AS INTEGER)) as total_occurrences",
            ],
        )
        fe_sql, fe_params = D1Q.aggregate(
            FRONTEND_EVENTS_TABLE,
            expressions=[
                "COUNT(*) as total",
                "SUM(CASE WHEN event_type = 'JS_ERROR' THEN 1 ELSE 0 END) as js_errors",
                "SUM(CASE WHEN event_type = 'NETWORK_ERROR' THEN 1 ELSE 0 END) as network_errors",
            ],
            where_clause="last_seen >= datetime('now', '-24 hours')",
        )

        from ..models import _int  # noqa: PLC0415
        srv_row = (client.execute(srv_sql, srv_params).results or [{}])[0]
        fe_row = (client.execute(fe_sql, fe_params).results or [{}])[0]
        return CombinedStats(
            open_errors=_int(srv_row.get("open_errors")),
            resolved=_int(srv_row.get("resolved")),
            total_occurrences=_int(srv_row.get("total_occurrences")),
            fe_total_24h=_int(fe_row.get("total")),
            fe_js_errors_24h=_int(fe_row.get("js_errors")),
            fe_network_errors_24h=_int(fe_row.get("network_errors")),
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Users
    # ─────────────────────────────────────────────────────────────────────────

    def get_users(
        self,
        *,
        api_url: str | None = None,
        is_active: bool | None = None,
        search: str | None = None,
        limit: int = 200,
    ) -> list[D1User]:
        conditions: dict[str, Any] = {}
        if api_url:
            conditions["api_url"] = api_url
        if is_active is not None:
            conditions["is_active"] = "1" if is_active else "0"

        if search:
            # Search requires LIKE — use select_raw with equality conditions merged
            s = search.replace("'", "''")
            search_clause = (
                f"(email LIKE '%{s}%' OR first_name LIKE '%{s}%' "
                f"OR last_name LIKE '%{s}%' OR company LIKE '%{s}%')"
            )
            where_parts: list[str] = [f"{col} = ?" for col in conditions]
            where_parts.append(search_clause)
            sql, params = D1Q.select_raw(
                USERS_TABLE,
                where_clause=" AND ".join(where_parts),
                params=[str(v) for v in conditions.values()],
                order_by="date_joined DESC",
                limit=limit,
            )
        else:
            sql, params = D1Q.select(
                USERS_TABLE,
                conditions=conditions or None,
                order_by="date_joined DESC",
                limit=limit,
            )

        rows = self._client().execute(sql, params).results or []
        return [D1User.from_dict(r) for r in rows]

    def get_user_stats(self, api_url: str | None = None) -> D1UserStats:
        sql, params = D1Q.aggregate(
            USERS_TABLE,
            expressions=[
                "COUNT(*) as total",
                "SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active",
                "SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) as inactive",
            ],
            where_clause="api_url = ?" if api_url else None,
            params=[api_url] if api_url else None,
        )
        r = self._client().execute(sql, params)
        stats_row = (r.results or [{}])[0]
        projects_count = len(self.get_projects())
        return D1UserStats.from_rows(stats_row, projects_count)


__all__ = ["D1MonitorQuery"]
