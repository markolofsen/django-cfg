"""D1 table definition for log_events."""

from __future__ import annotations

from django_cfg.modules.django_cf.core import D1Column, D1Index, D1Q, D1Table

LOG_EVENTS_TABLE = D1Table(
    name="log_events",
    columns=[
        D1Column("fingerprint",      "TEXT", primary_key=True),
        D1Column("api_url",          "TEXT", not_null=True),
        D1Column("level",            "TEXT", not_null=True),
        D1Column("logger_name",      "TEXT", not_null=True),
        D1Column("message",          "TEXT", not_null=True),
        D1Column("module",           "TEXT", default="''"),
        D1Column("func_name",        "TEXT", default="''"),
        D1Column("pathname",         "TEXT", default="''"),
        D1Column("lineno",           "INTEGER", default="0"),
        D1Column("stack_trace",      "TEXT", default="''"),
        D1Column("extra",            "TEXT", default="'{}'"),
        D1Column("occurrence_count", "INTEGER", not_null=True, default="1"),
        D1Column("is_resolved",      "INTEGER", not_null=True, default="0"),
        D1Column("first_seen",       "TEXT", not_null=True),
        D1Column("last_seen",        "TEXT", not_null=True),
    ],
    pk=["fingerprint", "api_url"],
    indexes=[
        D1Index("idx_log_events_level", ("level", "last_seen")),
        D1Index("idx_log_events_logger", ("logger_name",)),
        D1Index("idx_log_events_resolved", ("is_resolved", "last_seen")),
    ],
    upsert_update=["occurrence_count", "last_seen", "is_resolved", "stack_trace", "extra"],
    upsert_conflict_target=["fingerprint", "api_url"],
)

SCHEMA_STATEMENTS = [
    D1Q.create_table(LOG_EVENTS_TABLE),
    *D1Q.create_indexes(LOG_EVENTS_TABLE),
]

__all__ = ["LOG_EVENTS_TABLE", "SCHEMA_STATEMENTS"]
