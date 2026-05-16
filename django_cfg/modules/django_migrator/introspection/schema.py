"""Read-only PostgreSQL schema introspection.

All queries hit ``information_schema`` — never DDL. Wraps cursor work
so the caller doesn't repeat boilerplate.
"""

from __future__ import annotations

from django.db import connections


class PostgresSchemaInspector:
    """Snapshot of tables and columns currently present on a DB alias.

    The snapshot is loaded lazily on first access and cached for the
    instance's lifetime — drift scans hit the same tables dozens of times,
    so caching saves a measurable amount of round-trips.
    """

    def __init__(self, alias: str) -> None:
        self._alias = alias
        self._tables: set[str] | None = None
        # table_name -> set of column_names (lazy per-table fetch)
        self._columns: dict[str, set[str]] = {}

    # --- Tables ---

    def tables(self) -> set[str]:
        """All table names in the current schema (cached)."""
        if self._tables is None:
            with connections[self._alias].cursor() as cursor:
                cursor.execute(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = current_schema()"
                )
                self._tables = {row[0] for row in cursor.fetchall()}
        return self._tables

    def table_exists(self, table_name: str) -> bool:
        return table_name in self.tables()

    # --- Columns ---

    def columns(self, table_name: str) -> set[str]:
        """All column names of ``table_name`` (cached per-table)."""
        cached = self._columns.get(table_name)
        if cached is not None:
            return cached
        with connections[self._alias].cursor() as cursor:
            cursor.execute(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = %s AND table_schema = current_schema()",
                [table_name],
            )
            cols = {row[0] for row in cursor.fetchall()}
        self._columns[table_name] = cols
        return cols

    def column_exists(self, table_name: str, column_name: str) -> bool:
        if not self.table_exists(table_name):
            return False
        return column_name in self.columns(table_name)

    # --- Cache invalidation ---

    def refresh(self) -> None:
        """Drop cached snapshot — call after applying migrations."""
        self._tables = None
        self._columns.clear()
