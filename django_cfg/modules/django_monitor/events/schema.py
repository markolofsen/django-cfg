"""
django_monitor.events.schema — D1 table definitions for monitor events.

All DDL/DML is generated via D1Q — no raw SQL strings.
"""

from __future__ import annotations

from django_cfg.modules.django_cf.core.d1_query import D1Column, D1Index, D1Q, D1Table

# ─────────────────────────────────────────────────────────────────────────────
# Table: server_events
# ─────────────────────────────────────────────────────────────────────────────

SERVER_EVENTS_TABLE = D1Table(
    name="server_events",
    columns=[
        D1Column("fingerprint",      "TEXT",    not_null=True),
        D1Column("api_url",          "TEXT",    not_null=True),
        D1Column("event_type",       "TEXT",    not_null=True),
        D1Column("level",            "TEXT",    not_null=True),
        D1Column("message",          "TEXT",    not_null=True, default="''"),
        D1Column("stack_trace",      "TEXT",    not_null=True, default="''"),
        D1Column("logger_name",      "TEXT",    not_null=True, default="''"),
        D1Column("url",              "TEXT",    not_null=True, default="''"),
        D1Column("http_method",      "TEXT",    not_null=True, default="''"),
        D1Column("http_status",      "INTEGER", not_null=False),
        D1Column("func_name",        "TEXT",    not_null=True, default="''"),
        D1Column("module",           "TEXT",    not_null=True, default="''"),
        D1Column("lineno",           "INTEGER", not_null=False),
        D1Column("extra",            "TEXT",    not_null=True, default="'{}'"),
        D1Column("occurrence_count", "INTEGER", not_null=True, default="1"),
        D1Column("is_resolved",      "INTEGER", not_null=True, default="0"),
        D1Column("first_seen",       "TEXT",    not_null=True),
        D1Column("last_seen",        "TEXT",    not_null=True),
        D1Column("synced_at",        "TEXT",    not_null=True),
    ],
    pk=["fingerprint", "api_url"],
    indexes=[
        D1Index("idx_se_api_url",  ("api_url", "last_seen")),
        D1Index("idx_se_resolved", ("is_resolved", "last_seen")),
        D1Index("idx_se_type",     ("event_type", "last_seen")),
    ],
    # On conflict: update message/stack/last_seen, increment occurrence_count, reopen
    upsert_update=["message", "stack_trace", "last_seen", "synced_at"],
)

# ─────────────────────────────────────────────────────────────────────────────
# Table: frontend_events
# ─────────────────────────────────────────────────────────────────────────────

FRONTEND_EVENTS_TABLE = D1Table(
    name="frontend_events",
    columns=[
        D1Column("id",          "TEXT",    not_null=True),
        D1Column("api_url",     "TEXT",    not_null=True),
        D1Column("event_type",  "TEXT",    not_null=True),
        D1Column("level",       "TEXT",    not_null=True),
        D1Column("message",     "TEXT",    not_null=True, default="''"),
        D1Column("stack_trace", "TEXT",    not_null=True, default="''"),
        D1Column("url",         "TEXT",    not_null=True, default="''"),
        D1Column("http_status", "INTEGER", not_null=False),
        D1Column("http_method", "TEXT",    not_null=True, default="''"),
        D1Column("http_url",    "TEXT",    not_null=True, default="''"),
        D1Column("user_agent",  "TEXT",    not_null=True, default="''"),
        D1Column("ip_address",  "TEXT",    not_null=True, default="''"),
        D1Column("device_type", "TEXT",    not_null=True, default="''"),
        D1Column("os",          "TEXT",    not_null=True, default="''"),
        D1Column("browser",     "TEXT",    not_null=True, default="''"),
        D1Column("fingerprint", "TEXT",    not_null=True, default="''"),
        D1Column("user_id",     "TEXT",    not_null=False),
        D1Column("extra",       "TEXT",    not_null=True, default="'{}'"),
        D1Column("build_id",    "TEXT",    not_null=True, default="''"),
        D1Column("environment", "TEXT",    not_null=True, default="''"),
        D1Column("created_at",  "TEXT",    not_null=True),
    ],
    pk=["id", "api_url"],
    indexes=[
        D1Index("idx_fe_api_url",     ("api_url", "created_at")),
        D1Index("idx_fe_fingerprint", ("fingerprint", "api_url", "created_at")),
        D1Index("idx_fe_type",        ("event_type", "api_url", "created_at")),
        D1Index("idx_fe_user",        ("user_id", "api_url")),
    ],
    # INSERT OR IGNORE — no upsert_update needed
)

# ─────────────────────────────────────────────────────────────────────────────
# Schema statements (idempotent DDL)
# ─────────────────────────────────────────────────────────────────────────────

MONITOR_SCHEMA_STATEMENTS: list[str] = [
    D1Q.create_table(SERVER_EVENTS_TABLE),
    *D1Q.create_indexes(SERVER_EVENTS_TABLE),
    D1Q.create_table(FRONTEND_EVENTS_TABLE),
    *D1Q.create_indexes(FRONTEND_EVENTS_TABLE),
]


def ensure_monitor_schema(client: "CloudflareD1Client") -> None:  # type: ignore[name-defined]
    """Run all CREATE TABLE / CREATE INDEX statements idempotently."""
    from ..exceptions import MonitorSyncError
    for sql in MONITOR_SCHEMA_STATEMENTS:
        try:
            client.execute(sql)
        except Exception as exc:
            raise MonitorSyncError(
                f"django_monitor: schema migration failed: {exc}"
            ) from exc


__all__ = [
    "SERVER_EVENTS_TABLE",
    "FRONTEND_EVENTS_TABLE",
    "MONITOR_SCHEMA_STATEMENTS",
    "ensure_monitor_schema",
]
