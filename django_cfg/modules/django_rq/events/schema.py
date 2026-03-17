"""
django_rq.events.schema — D1 table definitions for RQ job events and worker heartbeats.

All DDL/DML is generated via D1Q — no raw SQL strings.
"""

from __future__ import annotations

from django_cfg.modules.django_cf.core.d1_query import D1Column, D1Index, D1Q, D1Table

# ─────────────────────────────────────────────────────────────────────────────
# Table: rq_job_events
# ─────────────────────────────────────────────────────────────────────────────

RQ_JOB_EVENTS_TABLE = D1Table(
    name="rq_job_events",
    columns=[
        D1Column("id",               "TEXT",    not_null=True),   # UUID — primary key
        D1Column("job_id",           "TEXT",    not_null=True),
        D1Column("queue",            "TEXT",    not_null=True),
        D1Column("func_name",        "TEXT",    not_null=True,  default="''"),
        D1Column("event_type",       "TEXT",    not_null=True),   # JOB_QUEUED|JOB_STARTED|JOB_FINISHED|JOB_FAILED|JOB_CANCELED
        D1Column("status",           "TEXT",    not_null=True),   # queued|started|finished|failed|canceled
        D1Column("worker_name",      "TEXT",    not_null=False),
        D1Column("error_message",    "TEXT",    not_null=False),  # max 2KB
        D1Column("stack_trace",      "TEXT",    not_null=False),  # max 10KB
        D1Column("duration_seconds", "REAL",    not_null=False),
        D1Column("timeout_seconds",  "INTEGER", not_null=False),
        D1Column("extra",            "TEXT",    not_null=True,  default="'{}'"),  # JSON: args_preview, meta
        D1Column("created_at",       "TEXT",    not_null=True),
        D1Column("finished_at",      "TEXT",    not_null=False),
    ],
    pk=["id"],
    indexes=[
        D1Index("idx_rq_job_id",      ("job_id",)),
        D1Index("idx_rq_queue_time",  ("queue", "created_at")),
        D1Index("idx_rq_type_time",   ("event_type", "created_at")),
        D1Index("idx_rq_status_time", ("status", "created_at")),
    ],
)

# ─────────────────────────────────────────────────────────────────────────────
# Table: rq_worker_heartbeats
# ─────────────────────────────────────────────────────────────────────────────

RQ_WORKER_HEARTBEATS_TABLE = D1Table(
    name="rq_worker_heartbeats",
    columns=[
        D1Column("id",                         "TEXT",    not_null=True),   # UUID — primary key
        D1Column("worker_name",                "TEXT",    not_null=True),
        D1Column("queues",                     "TEXT",    not_null=True),   # comma-separated
        D1Column("state",                      "TEXT",    not_null=True),   # idle|busy|suspended
        D1Column("current_job_id",             "TEXT",    not_null=False),
        D1Column("successful_job_count",       "INTEGER", not_null=True,  default="0"),
        D1Column("failed_job_count",           "INTEGER", not_null=True,  default="0"),
        D1Column("total_working_time_seconds", "REAL",    not_null=True,  default="0"),
        D1Column("heartbeat_at",               "TEXT",    not_null=True),
    ],
    pk=["id"],
    indexes=[
        D1Index("idx_rq_worker_name", ("worker_name", "heartbeat_at")),
        D1Index("idx_rq_worker_time", ("heartbeat_at",)),
    ],
)

# ─────────────────────────────────────────────────────────────────────────────
# Schema statements (idempotent DDL)
# ─────────────────────────────────────────────────────────────────────────────

RQ_SCHEMA_STATEMENTS: list[str] = [
    D1Q.create_table(RQ_JOB_EVENTS_TABLE),
    *D1Q.create_indexes(RQ_JOB_EVENTS_TABLE),
    D1Q.create_table(RQ_WORKER_HEARTBEATS_TABLE),
    *D1Q.create_indexes(RQ_WORKER_HEARTBEATS_TABLE),
]


__all__ = [
    "RQ_JOB_EVENTS_TABLE",
    "RQ_WORKER_HEARTBEATS_TABLE",
    "RQ_SCHEMA_STATEMENTS",
]
