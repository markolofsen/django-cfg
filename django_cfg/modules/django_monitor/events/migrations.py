"""
django_monitor.events.migrations — D1 schema migrations.

D1 (SQLite) does not support transactional DDL migrations like Django ORM.
Tables are created via CREATE TABLE IF NOT EXISTS (idempotent), but:
- Adding columns to existing tables requires ALTER TABLE ADD COLUMN
- Changing PK or removing columns requires DROP + CREATE (data loss)

Migrations are:
- Idempotent: errors for already-applied changes are silently ignored
- Run once per process: _applied flag prevents repeated HTTP calls
- Applied automatically on first push_*() call via MonitorSyncService._ensure_schema()

To add a new column:
1. Add D1Column to the table definition in schema.py
2. Add ALTER TABLE entry to D1_ALTER_MIGRATIONS with matching DDL
3. Deploy — next ingest request auto-applies the migration

To recreate a table (PK change, column removal):
1. Update the table definition in schema.py
2. Add table name to D1_RECREATE_TABLES
3. Deploy — table will be dropped and recreated (data loss!)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django_cfg.modules.django_cf.core.client import CloudflareD1Client

logger = logging.getLogger(__name__)

# Tables that must be dropped and recreated if their schema is incompatible.
# This is a one-time destructive migration — old data is lost.
# After recreation, remove from this list.
D1_RECREATE_TABLES: list[str] = [
    # v2.1.238: PK changed from (id, api_url) → (fingerprint, api_url),
    # added occurrence_count, first_seen, last_seen, fingerprint columns.
    # Old tables cannot be ALTERed — must recreate.
    "frontend_events",
]

# Additive column migrations (idempotent — "duplicate column" errors ignored)
D1_ALTER_MIGRATIONS: list[tuple[str, str]] = [
    # v2.1.238: occurrence_count for dedup
    ("server_events", "occurrence_count INTEGER NOT NULL DEFAULT 1"),
]

_applied = False


def apply_migrations(client: CloudflareD1Client) -> None:
    """Run schema migrations idempotently.

    1. Drop + recreate tables listed in D1_RECREATE_TABLES
    2. Run ALTER TABLE ADD COLUMN for D1_ALTER_MIGRATIONS

    Safe to call multiple times — skips after first successful run.
    """
    global _applied  # noqa: PLW0603
    if _applied:
        return

    from django_cfg.modules.django_cf.core.d1_query import D1Q
    from .schema import FRONTEND_EVENTS_TABLE

    # Step 1: Recreate tables with incompatible schemas
    for table_name in D1_RECREATE_TABLES:
        try:
            # Check if table needs recreation by testing for a new column
            client.execute(f"SELECT fingerprint FROM {table_name} LIMIT 0")
            # Column exists — table already has new schema
        except Exception as exc:
            if "no column" in str(exc).lower() or "has no column" in str(exc).lower() or "no such column" in str(exc).lower():
                logger.info("django_monitor: recreating %s (schema incompatible)", table_name)
                try:
                    client.execute(f"DROP TABLE IF EXISTS {table_name}")
                    if table_name == "frontend_events":
                        client.execute(D1Q.create_table(FRONTEND_EVENTS_TABLE))
                        for idx_sql in D1Q.create_indexes(FRONTEND_EVENTS_TABLE):
                            client.execute(idx_sql)
                    logger.info("django_monitor: %s recreated successfully", table_name)
                except Exception as create_exc:
                    logger.error("django_monitor: failed to recreate %s: %s", table_name, create_exc)
            else:
                logger.warning("django_monitor: probe %s failed: %s", table_name, exc)

    # Step 2: Additive column migrations
    for table, col_ddl in D1_ALTER_MIGRATIONS:
        col_name = col_ddl.split()[0]
        sql = f"ALTER TABLE {table} ADD COLUMN {col_ddl}"
        try:
            client.execute(sql)
            logger.info("django_monitor: migration applied — %s.%s", table, col_name)
        except Exception as exc:
            if "duplicate column" in str(exc).lower():
                pass
            else:
                logger.warning("django_monitor: migration failed — %s.%s: %s", table, col_name, exc)

    _applied = True


__all__ = ["D1_RECREATE_TABLES", "D1_ALTER_MIGRATIONS", "apply_migrations"]
