"""
django_grpc.events.types — Pydantic v2 row models for D1 tables.

Field names match D1 column names exactly so D1Q._extract() pulls
values directly from model_dump() — no manual to_params() methods.

2 enums:
  - GrpcRequestStatus
  - GrpcServerStatusValue

2 frozen row models:
  - GrpcRequestLogRow   → grpc_request_logs (append-only, 2-row pattern)
  - GrpcServerStatusRow → grpc_server_status (ephemeral heartbeat)

Removed (connection state tracking — tables were always empty, write path
was never wired from streaming handlers; state belongs in Redis/memory):
  - GrpcConnectionStatus enum
  - GrpcConnectionEventType enum
  - GrpcConnectionStateRow  (grpc_connection_states)
  - GrpcConnectionEventRow  (grpc_connection_events)
  - GrpcConnectionMetricRow (grpc_connection_metrics)
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_uuid() -> str:
    return str(uuid.uuid4())


# ─────────────────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────────────────

class GrpcRequestStatus(str, Enum):
    """Allowed values for grpc_request_logs.status column."""
    PENDING   = "pending"
    SUCCESS   = "success"
    ERROR     = "error"
    CANCELLED = "cancelled"
    TIMEOUT   = "timeout"


# GrpcConnectionStatus and GrpcConnectionEventType enums removed —
# belonged to grpc_connection_states / grpc_connection_events tables
# which were dead code (write path never called from streaming).

class GrpcServerStatusValue(str, Enum):
    """Allowed values for grpc_server_status.status column."""
    STARTING = "starting"
    RUNNING  = "running"
    STOPPING = "stopping"
    STOPPED  = "stopped"
    ERROR    = "error"


# ─────────────────────────────────────────────────────────────────────────────
# grpc_request_logs (append-only, 2-row pattern)
# ─────────────────────────────────────────────────────────────────────────────

class GrpcRequestLogRow(BaseModel):
    """Typed row for grpc_request_logs table (append-only).

    Two-row pattern per request:
      Row 1 (start):   status='pending', completed_at=None
      Row 2 (end):     status='success'|'error'|..., completed_at set

    Use class methods create_pending() and create_transition() for clarity.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    id:               str = Field(default_factory=_new_uuid)  # request_id UUID
    service_name:     str
    method_name:      str
    full_method:      str
    status:           str = GrpcRequestStatus.PENDING.value
    grpc_status_code: Optional[str] = None
    error_message:    Optional[str] = None
    error_details:    Optional[str] = None                    # JSON as TEXT
    duration_ms:      Optional[int] = None
    user_id:          Optional[int] = None                    # soft ref
    is_authenticated: int = 0
    client_ip:        Optional[str] = None
    created_at:       str = Field(default_factory=_now_iso)
    completed_at:     Optional[str] = None

    @classmethod
    def create_pending(
        cls,
        *,
        request_id: str,
        service_name: str,
        method_name: str,
        full_method: str,
        user_id: int | None = None,
        is_authenticated: bool = False,
        client_ip: str | None = None,
    ) -> "GrpcRequestLogRow":
        """Create the initial pending row at request start."""
        return cls(
            id=request_id,
            service_name=service_name,
            method_name=method_name,
            full_method=full_method,
            status=GrpcRequestStatus.PENDING.value,
            user_id=user_id,
            is_authenticated=int(is_authenticated),
            client_ip=client_ip,
        )

    @classmethod
    def create_transition(
        cls,
        *,
        request_id: str,
        service_name: str,
        method_name: str,
        full_method: str,
        status: GrpcRequestStatus,
        duration_ms: int | None = None,
        grpc_status_code: str | None = None,
        error_message: str | None = None,
        error_details: str | None = None,
        user_id: int | None = None,
        is_authenticated: bool = False,
        client_ip: str | None = None,
    ) -> "GrpcRequestLogRow":
        """Create the completion row (success/error/timeout/cancelled)."""
        now = _now_iso()
        return cls(
            id=request_id,
            service_name=service_name,
            method_name=method_name,
            full_method=full_method,
            status=status.value,
            grpc_status_code=grpc_status_code,
            error_message=error_message[:500] if error_message else None,
            error_details=error_details,
            duration_ms=duration_ms,
            user_id=user_id,
            is_authenticated=int(is_authenticated),
            client_ip=client_ip,
            created_at=now,
            completed_at=now,
        )


# ─────────────────────────────────────────────────────────────────────────────
# grpc_server_status (ephemeral heartbeat)
# ─────────────────────────────────────────────────────────────────────────────

class GrpcServerStatusRow(BaseModel):
    """Typed row for grpc_server_status table (upsert on heartbeat)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id:            str = Field(default_factory=_new_uuid)   # instance_id UUID
    host:          str
    port:          int
    address:       str
    pid:           int
    hostname:      str
    status:        str = GrpcServerStatusValue.STARTING.value
    error_message: Optional[str] = None
    started_at:    str = Field(default_factory=_now_iso)
    last_heartbeat: str = Field(default_factory=_now_iso)
    stopped_at:    Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# GrpcConnectionStateRow, GrpcConnectionEventRow, GrpcConnectionMetricRow —
# REMOVED. These 3 models mapped to tables that were always empty:
# the write path (services/connection_state/ CAS manager) was dead code —
# amark_connected_safe / amark_disconnected_safe / amark_error_safe were
# never called from streaming handlers. Removed together with the tables.
# ─────────────────────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────────────────────
# Parse helpers — convert raw D1 dicts → typed Pydantic rows
# ─────────────────────────────────────────────────────────────────────────────

def parse_request_log_row(row: dict) -> GrpcRequestLogRow:
    return GrpcRequestLogRow.model_validate(row)

def parse_server_status_row(row: dict) -> GrpcServerStatusRow:
    return GrpcServerStatusRow.model_validate(row)


__all__ = [
    # Enums
    "GrpcRequestStatus",
    "GrpcServerStatusValue",
    # Row models
    "GrpcRequestLogRow",
    "GrpcServerStatusRow",
    # Parse helpers
    "parse_request_log_row",
    "parse_server_status_row",
]
