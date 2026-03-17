"""
django_centrifugo.events.schema — D1 table definition for Centrifugo publish logs.

Append-only design: no UPDATE operations.
Status transitions (pending → success/failed/timeout/partial) are tracked
by inserting a new row per transition and reading the latest row per message_id.
"""

from __future__ import annotations

from django_cfg.modules.django_cf.core.d1_query import D1Column, D1Index, D1Q, D1Table

# ─────────────────────────────────────────────────────────────────────────────
# Table: centrifugo_logs
# ─────────────────────────────────────────────────────────────────────────────

CENTRIFUGO_LOGS_TABLE = D1Table(
    name="centrifugo_logs",
    columns=[
        D1Column("id",              "TEXT",    not_null=True),            # UUID — primary key
        D1Column("message_id",      "TEXT",    not_null=True),            # Unique publish identifier
        D1Column("channel",         "TEXT",    not_null=True),            # Centrifugo channel
        D1Column("data",            "TEXT",    not_null=True,  default="'{}'"),  # JSON payload as TEXT
        D1Column("wait_for_ack",    "INTEGER", not_null=True,  default="0"),     # BOOLEAN: 0=fire-and-forget, 1=ACK mode
        D1Column("ack_timeout",     "INTEGER", not_null=False),           # ACK timeout in seconds (nullable)
        D1Column("acks_received",   "INTEGER", not_null=True,  default="0"),
        D1Column("acks_expected",   "INTEGER", not_null=False),           # nullable
        D1Column("status",          "TEXT",    not_null=True,  default="'pending'"),  # pending|success|failed|timeout|partial
        D1Column("error_code",      "TEXT",    not_null=False),
        D1Column("error_message",   "TEXT",    not_null=False),
        D1Column("duration_ms",     "INTEGER", not_null=False),
        D1Column("is_notification", "INTEGER", not_null=True,  default="1"),     # BOOLEAN
        D1Column("user_id",         "TEXT",    not_null=False),           # Soft user reference (no FK)
        D1Column("caller_ip",       "TEXT",    not_null=False),
        D1Column("user_agent",      "TEXT",    not_null=False),
        D1Column("created_at",      "TEXT",    not_null=True),
        D1Column("completed_at",    "TEXT",    not_null=False),
    ],
    pk=["id"],
    indexes=[
        D1Index("idx_centrifugo_message_id", ("message_id",)),
        D1Index("idx_centrifugo_channel_ts", ("channel", "created_at")),
        D1Index("idx_centrifugo_status_ts",  ("status", "created_at")),
        D1Index("idx_centrifugo_ack_status", ("wait_for_ack", "status")),
        D1Index("idx_centrifugo_user_ts",    ("user_id", "created_at")),
    ],
)

# ─────────────────────────────────────────────────────────────────────────────
# Schema statements (idempotent DDL)
# ─────────────────────────────────────────────────────────────────────────────

CENTRIFUGO_SCHEMA_STATEMENTS: list[str] = [
    D1Q.create_table(CENTRIFUGO_LOGS_TABLE),
    *D1Q.create_indexes(CENTRIFUGO_LOGS_TABLE),
]


__all__ = [
    "CENTRIFUGO_LOGS_TABLE",
    "CENTRIFUGO_SCHEMA_STATEMENTS",
]
