"""
django_cf.services.d1_logs — Query logs from any D1 table.

Service layer for the d1_logs management command.
Builds parameterised SQL from structured query params, executes via
CloudflareD1Client, returns typed results.

Usage:
    from django_cfg.modules.django_cf.services.d1_logs import D1LogsService, D1LogQuery

    svc = D1LogsService()
    result = svc.query(D1LogQuery(table="server_events", level="error", since="1h", limit=20))
"""

from __future__ import annotations

import re
import time
from typing import Any, Literal

from pydantic import BaseModel, Field

from ..core.service import BaseD1Service

# ─────────────────────────────────────────────────────────────────────────────
# Known tables
# ─────────────────────────────────────────────────────────────────────────────

KNOWN_TABLES = (
    "server_events",
    "frontend_events",
    "grpc_request_logs",
    "grpc_server_status",
    "rq_job_events",
    "rq_worker_heartbeats",
    "centrifugo_logs",
    "log_events",
    "users",
    "projects",
)

# Per-table default ORDER BY (most useful column first).
_DEFAULT_ORDER: dict[str, str] = {
    "server_events":       "last_seen DESC",
    "frontend_events":     "last_seen DESC",
    "grpc_request_logs":   "created_at DESC",
    "grpc_server_status":  "last_heartbeat DESC",
    "rq_job_events":       "created_at DESC",
    "rq_worker_heartbeats": "heartbeat_at DESC",
    "centrifugo_logs":     "created_at DESC",
    "log_events":          "last_seen DESC",
    "users":               "updated_at DESC",
    "projects":            "synced_at DESC",
}

# Per-table time column for --since filter.
_TIME_COLUMN: dict[str, str] = {
    "server_events":       "last_seen",
    "frontend_events":     "last_seen",
    "grpc_request_logs":   "created_at",
    "grpc_server_status":  "last_heartbeat",
    "rq_job_events":       "created_at",
    "rq_worker_heartbeats": "heartbeat_at",
    "centrifugo_logs":     "created_at",
    "log_events":          "last_seen",
    "users":               "updated_at",
    "projects":            "synced_at",
}

# Per-table text-search columns for --search filter.
_SEARCH_COLUMNS: dict[str, list[str]] = {
    "server_events":       ["message", "stack_trace"],
    "frontend_events":     ["message", "stack_trace"],
    "grpc_request_logs":   ["error_message", "full_method"],
    "grpc_server_status":  ["error_message", "hostname"],
    "rq_job_events":       ["error_message", "func_name"],
    "rq_worker_heartbeats": ["worker_name"],
    "centrifugo_logs":     ["message"],
    "log_events":          ["message", "stack_trace", "logger_name"],
    "users":               ["email", "first_name", "last_name"],
    "projects":            ["project_name", "api_url"],
}


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic models
# ─────────────────────────────────────────────────────────────────────────────

class D1LogQuery(BaseModel):
    """Query parameters for D1 log retrieval."""

    table: Literal[
        "server_events", "frontend_events",
        "grpc_request_logs", "grpc_server_status",
        "rq_job_events", "rq_worker_heartbeats",
        "centrifugo_logs", "log_events",
        "users", "projects",
    ]
    limit: int = Field(default=50, ge=1, le=500)
    level: str | None = Field(default=None, description="Filter by level (error, warning, info)")
    since: str | None = Field(default=None, description="ISO datetime or relative: 1h, 24h, 7d")
    search: str | None = Field(default=None, description="Text search in message/error_message")
    method: str | None = Field(default=None, description="gRPC method name filter")
    status: str | None = Field(default=None, description="Status filter (pending, success, error)")
    sql: str | None = Field(default=None, description="Raw SQL WHERE clause (advanced)")
    format: Literal["table", "json", "compact"] = "table"


class D1LogResult(BaseModel):
    """Result of a D1 log query."""

    table: str
    query_sql: str
    entries: list[dict[str, Any]]
    total: int
    duration_ms: float


# ─────────────────────────────────────────────────────────────────────────────
# Service
# ─────────────────────────────────────────────────────────────────────────────

class D1LogsService(BaseD1Service):
    """Query logs from any D1 table."""

    def query(self, params: D1LogQuery) -> D1LogResult:
        """Build SQL from params, execute, return typed result."""
        where_clause, sql_params = self._build_where(params)

        order_by = _DEFAULT_ORDER.get(params.table, "rowid DESC")
        col_expr = "*"
        sql = f"SELECT {col_expr} FROM {params.table}"
        if where_clause:
            sql += f" WHERE {where_clause}"
        sql += f" ORDER BY {order_by}"
        sql += f" LIMIT {params.limit}"

        client = self._get_client()
        t0 = time.monotonic()
        result = client.execute(sql, sql_params or None)
        duration_ms = round((time.monotonic() - t0) * 1000, 1)

        return D1LogResult(
            table=params.table,
            query_sql=sql,
            entries=result.results or [],
            total=len(result.results or []),
            duration_ms=duration_ms,
        )

    def get_table_stats(self) -> dict[str, int]:
        """Row counts for all known tables."""
        client = self._get_client()
        stats: dict[str, int] = {}
        for table_name in KNOWN_TABLES:
            try:
                result = client.execute(f"SELECT COUNT(*) as cnt FROM {table_name}")
                cnt = result.results[0].get("cnt", 0) if result.results else 0
                stats[table_name] = int(cnt)
            except Exception:
                stats[table_name] = -1  # table may not exist
        return stats

    # ── Internal ──────────────────────────────────────────────────────────────

    def _build_where(self, params: D1LogQuery) -> tuple[str, list[str]]:
        """Build WHERE clause + params from query filters."""
        parts: list[str] = []
        sql_params: list[str] = []

        # --level
        if params.level:
            parts.append("level = ?")
            sql_params.append(params.level)

        # --since
        if params.since:
            time_col = _TIME_COLUMN.get(params.table, "created_at")
            since_expr, since_params = self._parse_since(params.since, time_col)
            parts.append(since_expr)
            sql_params.extend(since_params)

        # --search
        if params.search:
            search_cols = _SEARCH_COLUMNS.get(params.table, ["message"])
            like_parts = [f"{col} LIKE ?" for col in search_cols]
            parts.append(f"({' OR '.join(like_parts)})")
            for _ in search_cols:
                sql_params.append(f"%{params.search}%")

        # --method (gRPC tables only)
        if params.method:
            parts.append("method_name LIKE ?")
            sql_params.append(f"%{params.method}%")

        # --status
        if params.status:
            parts.append("status = ?")
            sql_params.append(params.status)

        # --sql (raw WHERE clause — advanced, appended as-is)
        if params.sql:
            parts.append(f"({params.sql})")

        where_clause = " AND ".join(parts) if parts else ""
        return where_clause, sql_params

    @staticmethod
    def _parse_since(since: str, time_col: str) -> tuple[str, list[str]]:
        """Convert '1h', '24h', '7d' or ISO datetime to SQL WHERE fragment.

        Returns (where_fragment, params).
        """
        # Relative: 1h, 24h, 7d, 30m
        match = re.match(r"^(\d+)([hHdDmM])$", since)
        if match:
            value = int(match.group(1))
            unit = match.group(2).lower()
            if unit == "h":
                modifier = f"-{value} hours"
            elif unit == "d":
                modifier = f"-{value} days"
            elif unit == "m":
                modifier = f"-{value} minutes"
            else:
                modifier = f"-{value} hours"
            return f"{time_col} >= datetime('now', ?)", [modifier]

        # Absolute ISO datetime — passed as-is
        return f"{time_col} >= ?", [since]


__all__ = ["D1LogQuery", "D1LogResult", "D1LogsService", "KNOWN_TABLES"]
