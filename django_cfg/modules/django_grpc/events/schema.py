"""
django_grpc.events.schema — D1 table definitions for gRPC module.

2 active tables:
  - grpc_request_logs  — Request audit log (append-only)
  - grpc_server_status — gRPC server heartbeat (ephemeral, upsert)

Removed tables (write path was dead code — tables always empty):
  - grpc_connection_states  — Bot connection state (optimistic locking)
  - grpc_connection_events  — Connection event log (append-only)
  - grpc_connection_metrics — Network metrics time-series (append-only)
  Connection state tracking belongs in Redis/memory, not D1.

All timestamps: ISO 8601 TEXT. No foreign keys — soft references via TEXT/INTEGER.
All DDL is idempotent (CREATE TABLE IF NOT EXISTS, CREATE INDEX IF NOT EXISTS).
"""

from __future__ import annotations

from django_cfg.modules.django_cf.core.d1_query import D1Column, D1Index, D1Q, D1Table

# ─────────────────────────────────────────────────────────────────────────────
# grpc_request_logs (append-only)
# ─────────────────────────────────────────────────────────────────────────────

GRPC_REQUEST_LOGS_TABLE = D1Table(
    name="grpc_request_logs",
    columns=[
        D1Column("id",               "TEXT",    not_null=True),        # request_id UUID
        D1Column("service_name",     "TEXT",    not_null=True),
        D1Column("method_name",      "TEXT",    not_null=True),
        D1Column("full_method",      "TEXT",    not_null=True),
        D1Column("status",           "TEXT",    not_null=True,  default="'pending'"),
        D1Column("grpc_status_code", "TEXT",    not_null=False),
        D1Column("error_message",    "TEXT",    not_null=False),
        D1Column("error_details",    "TEXT",    not_null=False),       # JSON as TEXT
        D1Column("duration_ms",      "INTEGER", not_null=False),
        D1Column("user_id",          "INTEGER", not_null=False),       # soft ref
        D1Column("is_authenticated", "INTEGER", not_null=True,  default="0"),
        D1Column("client_ip",        "TEXT",    not_null=False),
        D1Column("created_at",       "TEXT",    not_null=True),
        D1Column("completed_at",     "TEXT",    not_null=False),
    ],
    pk=["id"],
    indexes=[
        D1Index("idx_grpc_req_service", ("service_name", "created_at")),
        D1Index("idx_grpc_req_status",  ("status", "created_at")),
        D1Index("idx_grpc_req_user",    ("user_id", "created_at")),
    ],
)

# ─────────────────────────────────────────────────────────────────────────────
# grpc_server_status (ephemeral, upsert on heartbeat)
# ─────────────────────────────────────────────────────────────────────────────

GRPC_SERVER_STATUS_TABLE = D1Table(
    name="grpc_server_status",
    columns=[
        D1Column("id",             "TEXT",    not_null=True),          # instance_id UUID
        D1Column("host",           "TEXT",    not_null=True),
        D1Column("port",           "INTEGER", not_null=True),
        D1Column("address",        "TEXT",    not_null=True),
        D1Column("pid",            "INTEGER", not_null=True),
        D1Column("hostname",       "TEXT",    not_null=True),
        D1Column("status",         "TEXT",    not_null=True),          # starting|running|stopping|stopped|error
        D1Column("error_message",  "TEXT",    not_null=False),
        D1Column("started_at",     "TEXT",    not_null=True),
        D1Column("last_heartbeat", "TEXT",    not_null=True),
        D1Column("stopped_at",     "TEXT",    not_null=False),
    ],
    pk=["id"],
    indexes=[
        D1Index("idx_grpc_server_status", ("status",)),
    ],
    upsert_update=["status", "error_message", "last_heartbeat", "stopped_at"],
    upsert_conflict_target=["id"],
)

# ─────────────────────────────────────────────────────────────────────────────
# GRPC_CONNECTION_STATES_TABLE, GRPC_CONNECTION_EVENTS_TABLE,
# GRPC_CONNECTION_METRICS_TABLE — REMOVED
#
# All 3 tables dropped because the write path was never connected:
# services/connection_state/ (amark_connected_safe etc.) was dead code and
# has been deleted. The tables were always empty in production.
# Connection state tracking belongs in Redis / in-process memory, not D1.
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# Schema statements — idempotent DDL (CREATE TABLE IF NOT EXISTS + indexes)
# ─────────────────────────────────────────────────────────────────────────────

GRPC_SCHEMA_STATEMENTS: list[str] = [
    D1Q.create_table(GRPC_REQUEST_LOGS_TABLE),
    *D1Q.create_indexes(GRPC_REQUEST_LOGS_TABLE),
    D1Q.create_table(GRPC_SERVER_STATUS_TABLE),
    *D1Q.create_indexes(GRPC_SERVER_STATUS_TABLE),
]


__all__ = [
    "GRPC_REQUEST_LOGS_TABLE",
    "GRPC_SERVER_STATUS_TABLE",
    "GRPC_SCHEMA_STATEMENTS",
]
