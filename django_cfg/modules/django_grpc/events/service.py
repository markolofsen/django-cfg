"""
django_grpc.events.service — GrpcD1Service.

Single persistence service for gRPC D1 tables.
Inherits shared client, api_url resolution, and schema management
from BaseD1Service — no separate credentials needed.

Write operations:
  - grpc_request_logs:  insert_request_log, batch_insert_request_logs
  - grpc_server_status: upsert_server_status

Read operations (for Streamlit dashboard):
  - get_recent_request_logs, get_request_stats
  - get_server_status
"""

from __future__ import annotations

import logging
from typing import Optional

from django_cfg.modules.django_cf.core import BaseD1Service
from django_cfg.modules.django_cf.core.d1_query import D1Q

from ..exceptions import DjangoGrpcSyncError
from .schema import (
    GRPC_REQUEST_LOGS_TABLE,
    GRPC_SCHEMA_STATEMENTS,
    GRPC_SERVER_STATUS_TABLE,
)
from .types import (
    GrpcRequestLogRow,
    GrpcServerStatusRow,
    parse_request_log_row,
    parse_server_status_row,
)

logger = logging.getLogger(__name__)


class GrpcD1Service(BaseD1Service):
    """Handles all D1 read/write operations for the gRPC module."""

    def _get_schema_statements(self) -> list[str]:
        return GRPC_SCHEMA_STATEMENTS

    # ─────────────────────────────────────────────────────────────────────────
    # Request Logs (append-only)
    # ─────────────────────────────────────────────────────────────────────────

    def insert_request_log(self, row: GrpcRequestLogRow) -> None:
        """Insert a single request log row (append-only)."""
        self._ensure_schema()
        sql, params = D1Q.insert_ignore(GRPC_REQUEST_LOGS_TABLE, row)
        try:
            self._get_client().execute(sql, params)
        except Exception as exc:
            raise DjangoGrpcSyncError(
                f"insert_request_log failed: {exc}", original_error=exc,
            ) from exc

    def batch_insert_request_logs(self, rows: list[GrpcRequestLogRow]) -> None:
        """Batch insert request logs via D1 batch() API. Used by log worker."""
        if not rows:
            return
        self._ensure_schema()
        client = self._get_client()
        statements = []
        for row in rows:
            sql, params = D1Q.insert_ignore(GRPC_REQUEST_LOGS_TABLE, row)
            statements.append({"sql": sql, "params": params})
        try:
            client.execute_batch(statements)
            logger.debug("batch_insert_request_logs: %d rows", len(rows))
        except Exception as exc:
            raise DjangoGrpcSyncError(
                f"batch_insert_request_logs failed: {exc}", original_error=exc,
            ) from exc

    def get_recent_request_logs(
        self,
        *,
        hours: int = 24,
        limit: int = 200,
        offset: int = 0,
        status: Optional[str] = None,
        service: Optional[str] = None,
    ) -> list[GrpcRequestLogRow]:
        """Return paginated request logs for the dashboard."""
        self._ensure_schema()
        where_clause = f"created_at > datetime('now', '-{int(hours)} hours')"
        extra_params: list = []
        if status:
            where_clause += " AND status = ?"
            extra_params.append(status)
        if service:
            where_clause += " AND service_name = ?"
            extra_params.append(service)
        sql, params = D1Q.select_raw(
            GRPC_REQUEST_LOGS_TABLE,
            where_clause=where_clause,
            params=extra_params,
            order_by="created_at DESC",
            limit=limit,
        )
        if offset:
            sql += f" OFFSET {int(offset)}"
        try:
            result = self._get_client().execute(sql, params)
            return [parse_request_log_row(r) for r in (result.results or [])]
        except Exception as exc:
            raise DjangoGrpcSyncError(
                f"get_recent_request_logs failed: {exc}", original_error=exc,
            ) from exc

    def get_request_stats(self, *, hours: int = 24) -> dict:
        """Return aggregate KPIs for the overview dashboard."""
        self._ensure_schema()
        sql = (
            "SELECT "
            "  COUNT(*) AS total, "
            "  SUM(CASE WHEN status='success'   THEN 1 ELSE 0 END) AS success_count, "
            "  SUM(CASE WHEN status='error'     THEN 1 ELSE 0 END) AS error_count, "
            "  SUM(CASE WHEN status='timeout'   THEN 1 ELSE 0 END) AS timeout_count, "
            "  SUM(CASE WHEN status='cancelled' THEN 1 ELSE 0 END) AS cancelled_count, "
            "  SUM(CASE WHEN status='pending'   THEN 1 ELSE 0 END) AS pending_count, "
            "  AVG(duration_ms) AS avg_duration_ms "
            "FROM grpc_request_logs "
            f"WHERE created_at > datetime('now', '-{int(hours)} hours')"
        )
        try:
            result = self._get_client().execute(sql)
            rows = result.results or []
            return rows[0] if rows else {}
        except Exception as exc:
            raise DjangoGrpcSyncError(
                f"get_request_stats failed: {exc}", original_error=exc,
            ) from exc

    # ─────────────────────────────────────────────────────────────────────────
    # Server Status
    # ─────────────────────────────────────────────────────────────────────────

    def upsert_server_status(self, row: GrpcServerStatusRow) -> None:
        """Upsert server heartbeat row."""
        self._ensure_schema()
        sql, params = D1Q.upsert(GRPC_SERVER_STATUS_TABLE, row)
        try:
            self._get_client().execute(sql, params)
        except Exception as exc:
            raise DjangoGrpcSyncError(
                f"upsert_server_status failed: {exc}", original_error=exc,
            ) from exc

    def get_server_status(self) -> list[GrpcServerStatusRow]:
        """Return all server status rows for the dashboard."""
        self._ensure_schema()
        sql, params = D1Q.select(GRPC_SERVER_STATUS_TABLE, order_by="started_at DESC")
        try:
            result = self._get_client().execute(sql, params)
            return [parse_server_status_row(r) for r in (result.results or [])]
        except Exception as exc:
            raise DjangoGrpcSyncError(
                f"get_server_status failed: {exc}", original_error=exc,
            ) from exc

    # ─────────────────────────────────────────────────────────────────────────
    # Connection States / Events / Metrics — REMOVED
    #
    # These 3 tables (grpc_connection_states, grpc_connection_events,
    # grpc_connection_metrics) and all their read/write methods were deleted
    # because the write path was never wired up:
    #
    #   services/connection_state/ (amark_connected_safe / amark_disconnected_safe
    #   / amark_error_safe) was dead code — never called from streaming handlers.
    #   The tables were always empty in production.
    #
    # Connection state tracking belongs in Redis / in-process memory, not D1.
    # D1 in this module is for append-only audit logs (request_logs) and the
    # ephemeral server heartbeat (server_status) — both are still active.
    #
    # Removed methods:
    #   upsert_connection_state, update_connection_state_optimistic,
    #   get_connection_state_summary, get_connection_states,
    #   get_connection_state_by_machine, insert_connection_event,
    #   get_connection_events, insert_connection_metric, get_connection_metrics
    # ─────────────────────────────────────────────────────────────────────────


__all__ = ["GrpcD1Service"]
