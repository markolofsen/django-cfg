"""
django_cf.core.d1_query — D1 SQL factory.

Single source of truth for all D1 DML/DDL/SELECT.

Concepts
--------
D1Column
    Declares one column: name, type, constraints.

D1Table
    Describes a complete table: columns, primary key, indexes,
    conflict strategy for upsert.

D1Q (D1Query)
    Stateless SQL factory.  Given a D1Table + a Pydantic model
    instance (or plain dict), generates (sql, params) tuples ready
    for CloudflareD1Client.execute().

Usage
-----
    from django_cfg.modules.django_cf.core.d1_query import D1Q, D1Column, D1Table

    PROJECTS_TABLE = D1Table(
        name="projects",
        columns=[
            D1Column("api_url",      "TEXT",    primary_key=True),
            D1Column("project_name", "TEXT",    not_null=True, default="''"),
            D1Column("synced_at",    "TEXT",    not_null=True),
        ],
        upsert_update=["project_name", "synced_at"],
    )

    # DDL
    sql = D1Q.create_table(PROJECTS_TABLE)
    for sql in D1Q.create_indexes(PROJECTS_TABLE):
        client.execute(sql)

    # DML
    sql, params = D1Q.upsert(PROJECTS_TABLE, data)        # INSERT … ON CONFLICT … DO UPDATE
    sql, params = D1Q.insert_ignore(PROJECTS_TABLE, data) # INSERT OR IGNORE …
    sql, params = D1Q.delete_where(PROJECTS_TABLE, {"is_resolved": "1", "api_url": url})

    # SELECT — typed queries, no raw SQL needed in service layer
    sql, params = D1Q.select(PROJECTS_TABLE, order_by="project_name")
    sql, params = D1Q.select(SERVER_EVENTS_TABLE,
                             conditions={"is_resolved": "0", "api_url": url},
                             order_by="last_seen DESC", limit=100)
    sql, params = D1Q.select_raw(FRONTEND_EVENTS_TABLE,
                                 where_clause="created_at >= datetime('now', ? || ' hours')",
                                 params=["-24"], order_by="created_at DESC", limit=200)
    sql, params = D1Q.aggregate(SERVER_EVENTS_TABLE, expressions=[
        "SUM(CASE WHEN is_resolved = 0 THEN 1 ELSE 0 END) as open_errors",
        "SUM(occurrence_count) as total_occurrences",
    ])
    sql, params = D1Q.group_by(FRONTEND_EVENTS_TABLE, select_expr="event_type, COUNT(*) as count",
                               group_by="event_type", order_by="count DESC",
                               where_clause="created_at >= datetime('now', ? || ' hours')",
                               params=["-24"])
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ─────────────────────────────────────────────────────────────────────────────
# Column descriptor
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class D1Column:
    """Describes a single D1 (SQLite) column."""

    name: str
    col_type: str = "TEXT"              # TEXT | INTEGER | REAL | BLOB
    not_null: bool = True
    default: str | None = None          # raw SQL default, e.g. "''" or "1" or "0"
    primary_key: bool = False           # single-column PK; use D1Table.pk for composite


    def ddl(self) -> str:
        parts = [self.name, self.col_type]
        if self.primary_key:
            parts.append("PRIMARY KEY")
        elif self.not_null:
            parts.append("NOT NULL")
        if self.default is not None:
            parts.append(f"DEFAULT {self.default}")
        return " ".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# Index descriptor
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class D1Index:
    """Describes a CREATE INDEX statement."""

    name: str                           # index name, e.g. "idx_users_email"
    columns: tuple[str, ...]            # columns to index

    def ddl(self, table_name: str) -> str:
        cols = ", ".join(self.columns)
        return f"CREATE INDEX IF NOT EXISTS {self.name} ON {table_name}({cols})"


# ─────────────────────────────────────────────────────────────────────────────
# Table descriptor
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class D1Table:
    """Describes a complete D1 table.

    Parameters
    ----------
    name:
        Table name.
    columns:
        All columns in declaration order.  This order also determines
        the parameter order in INSERT statements — it is the single
        source of truth.
    pk:
        Composite primary key column names.  Leave empty if a column
        already has ``primary_key=True``.
    indexes:
        Additional indexes (beyond the implicit PK).
    upsert_update:
        Column names to update on conflict (DO UPDATE SET).
        If empty, upsert falls back to INSERT OR IGNORE.
    upsert_conflict_target:
        Columns to use in ON CONFLICT(…).  Defaults to pk or the
        single-column PK if not set.
    """

    name: str
    columns: list[D1Column]
    pk: list[str] = field(default_factory=list)
    indexes: list[D1Index] = field(default_factory=list)
    upsert_update: list[str] = field(default_factory=list)
    upsert_conflict_target: list[str] = field(default_factory=list)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _pk_cols(self) -> list[str]:
        if self.pk:
            return self.pk
        return [c.name for c in self.columns if c.primary_key]

    def _conflict_target(self) -> list[str]:
        if self.upsert_conflict_target:
            return self.upsert_conflict_target
        return self._pk_cols()

    @property
    def column_names(self) -> list[str]:
        return [c.name for c in self.columns]


# ─────────────────────────────────────────────────────────────────────────────
# SQL factory
# ─────────────────────────────────────────────────────────────────────────────

class D1Q:
    """Stateless D1 SQL factory.

    All methods are class-methods — no instantiation needed.

    Parameter extraction
    --------------------
    ``data`` can be:
    - a Pydantic BaseModel  — values pulled via ``model_dump()``
    - a dataclass           — values pulled via ``__dict__``
    - a plain dict

    Only the columns declared in the table are used; extra keys are
    silently ignored.  Missing keys raise ``KeyError``.
    """

    # ── DDL ───────────────────────────────────────────────────────────────────

    @classmethod
    def create_table(cls, table: D1Table) -> str:
        """Generate CREATE TABLE IF NOT EXISTS …"""
        col_ddls = [c.ddl() for c in table.columns]
        pk_cols = table._pk_cols()
        if len(pk_cols) > 1:
            col_ddls.append(f"PRIMARY KEY ({', '.join(pk_cols)})")
        col_block = ",\n    ".join(col_ddls)
        return f"CREATE TABLE IF NOT EXISTS {table.name} (\n    {col_block}\n)"

    @classmethod
    def create_indexes(cls, table: D1Table) -> list[str]:
        """Generate all CREATE INDEX IF NOT EXISTS … for the table's indexes."""
        return [idx.ddl(table.name) for idx in table.indexes]

    # ── DML ───────────────────────────────────────────────────────────────────

    @classmethod
    def upsert(cls, table: D1Table, data: Any) -> tuple[str, list[str]]:
        """INSERT … ON CONFLICT … DO UPDATE SET …

        ``upsert_update`` must be set on the table.
        Returns (sql, params).
        """
        if not table.upsert_update:
            raise ValueError(
                f"D1Q.upsert: table '{table.name}' has no upsert_update columns defined"
            )
        values = cls._extract(table, data)
        cols = table.column_names
        placeholders = ", ".join("?" * len(cols))
        col_list = ", ".join(cols)
        conflict = ", ".join(table._conflict_target())
        updates = ",\n    ".join(
            f"{col} = excluded.{col}" for col in table.upsert_update
        )
        sql = (
            f"INSERT INTO {table.name} ({col_list})\n"
            f"VALUES ({placeholders})\n"
            f"ON CONFLICT({conflict}) DO UPDATE SET\n"
            f"    {updates}"
        )
        return sql, values

    @classmethod
    def upsert_increment(
        cls,
        table: D1Table,
        data: Any,
        increment_col: str,
        reset_cols: dict[str, str] | None = None,
    ) -> tuple[str, list[str]]:
        """INSERT … ON CONFLICT … DO UPDATE SET … with an increment + optional resets.

        Used for server_events where occurrence_count increments on every upsert.

        Parameters
        ----------
        increment_col:
            Column to increment (``col = col + 1``).
        reset_cols:
            Dict of ``{col: literal_value}`` to reset on conflict,
            e.g. ``{"is_resolved": "0"}``.
        """
        if not table.upsert_update:
            raise ValueError(
                f"D1Q.upsert_increment: table '{table.name}' has no upsert_update columns defined"
            )
        values = cls._extract(table, data)
        cols = table.column_names
        placeholders = ", ".join("?" * len(cols))
        col_list = ", ".join(cols)
        conflict = ", ".join(table._conflict_target())

        update_parts = [
            f"{col} = excluded.{col}" for col in table.upsert_update
        ]
        update_parts.append(
            f"{increment_col} = {table.name}.{increment_col} + 1"
        )
        for col, val in (reset_cols or {}).items():
            update_parts.append(f"{col} = {val}")

        updates = ",\n    ".join(update_parts)
        sql = (
            f"INSERT INTO {table.name} ({col_list})\n"
            f"VALUES ({placeholders})\n"
            f"ON CONFLICT({conflict}) DO UPDATE SET\n"
            f"    {updates}"
        )
        return sql, values

    @classmethod
    def upsert_increment_batch(
        cls,
        table: D1Table,
        rows: list[Any],
        increment_col: str,
        reset_cols: dict[str, str] | None = None,
    ) -> tuple[str, list[str]]:
        """Multi-row INSERT … ON CONFLICT … DO UPDATE SET … — one SQL, one HTTP request.

        Generates a single statement with N rows in VALUES:
            INSERT INTO t (c1, c2, ...) VALUES (?,?,...), (?,?,...), ...
            ON CONFLICT(...) DO UPDATE SET ...

        Parameters
        ----------
        rows:
            List of Pydantic models, dataclasses, or dicts — one per row.
        increment_col:
            Column to increment on conflict (``col = col + 1``).
        reset_cols:
            Dict of ``{col: literal_value}`` to reset on conflict.
        """
        if not rows:
            raise ValueError("upsert_increment_batch: rows must not be empty")
        if not table.upsert_update:
            raise ValueError(
                f"D1Q.upsert_increment_batch: table '{table.name}' has no upsert_update columns defined"
            )

        cols = table.column_names
        col_list = ", ".join(cols)
        conflict = ", ".join(table._conflict_target())
        row_placeholder = f"({', '.join('?' * len(cols))})"

        all_values: list[str] = []
        value_rows: list[str] = []
        for row in rows:
            all_values.extend(cls._extract(table, row))
            value_rows.append(row_placeholder)

        update_parts = [f"{col} = excluded.{col}" for col in table.upsert_update]
        update_parts.append(f"{increment_col} = {table.name}.{increment_col} + 1")
        for col, val in (reset_cols or {}).items():
            update_parts.append(f"{col} = {val}")

        updates = ",\n    ".join(update_parts)
        sql = (
            f"INSERT INTO {table.name} ({col_list})\n"
            f"VALUES {', '.join(value_rows)}\n"
            f"ON CONFLICT({conflict}) DO UPDATE SET\n"
            f"    {updates}"
        )
        return sql, all_values

    @classmethod
    def insert_ignore(cls, table: D1Table, data: Any) -> tuple[str, list[str]]:
        """INSERT OR IGNORE INTO … — idempotent, silently skips duplicates."""
        values = cls._extract(table, data)
        cols = table.column_names
        placeholders = ", ".join("?" * len(cols))
        col_list = ", ".join(cols)
        sql = (
            f"INSERT OR IGNORE INTO {table.name} ({col_list})\n"
            f"VALUES ({placeholders})"
        )
        return sql, values

    @classmethod
    def delete_where(
        cls,
        table: D1Table,
        conditions: dict[str, Any],
    ) -> tuple[str, list[str]]:
        """DELETE FROM … WHERE col = ? AND …

        ``conditions`` is an ordered dict of {column: value}.
        Values are passed as params (safe, no injection).
        For SQL expressions (e.g. datetime comparisons) use
        ``delete_where_raw`` instead.
        """
        where_parts = [f"{col} = ?" for col in conditions]
        params = [str(v) for v in conditions.values()]
        sql = f"DELETE FROM {table.name} WHERE {' AND '.join(where_parts)}"
        return sql, params

    @classmethod
    def delete_where_raw(
        cls,
        table: D1Table,
        where_clause: str,
        params: list[str],
    ) -> tuple[str, list[str]]:
        """DELETE FROM … WHERE <raw_clause> with explicit params.

        Use only for expressions not expressible via delete_where,
        e.g. ``"last_seen < datetime('now', ? || ' days')"``
        """
        sql = f"DELETE FROM {table.name} WHERE {where_clause}"
        return sql, params

    # ── SELECT ────────────────────────────────────────────────────────────────

    @classmethod
    def select(
        cls,
        table: D1Table,
        *,
        conditions: dict[str, Any] | None = None,
        columns: list[str] | None = None,
        order_by: str | None = None,
        limit: int | None = None,
    ) -> tuple[str, list[str]]:
        """SELECT … FROM … WHERE col = ? AND … ORDER BY … LIMIT …

        Parameters
        ----------
        conditions:
            Equality conditions: ``{"col": value, ...}``.
            Values become ``?`` params (injection-safe).
            For non-equality expressions use ``select_raw``.
        columns:
            Columns to select.  Defaults to ``*``.
        order_by:
            Raw ORDER BY expression, e.g. ``"last_seen DESC"``.
        limit:
            LIMIT N.  Omitted if None.
        """
        col_expr = ", ".join(columns) if columns else "*"
        sql = f"SELECT {col_expr} FROM {table.name}"
        params: list[str] = []

        if conditions:
            where_parts = [f"{col} = ?" for col in conditions]
            params = [str(v) for v in conditions.values()]
            sql += " WHERE " + " AND ".join(where_parts)

        if order_by:
            sql += f" ORDER BY {order_by}"
        if limit is not None:
            sql += f" LIMIT {limit}"

        return sql, params

    @classmethod
    def select_raw(
        cls,
        table: D1Table,
        *,
        where_clause: str | None = None,
        params: list[str] | None = None,
        columns: list[str] | None = None,
        order_by: str | None = None,
        limit: int | None = None,
    ) -> tuple[str, list[str]]:
        """SELECT with a raw WHERE clause for SQL expressions.

        Use when conditions include functions/operators that cannot
        be expressed as simple equality, e.g.:
            ``where_clause="created_at >= datetime('now', ? || ' hours')"``
            ``params=["-24"]``
        """
        col_expr = ", ".join(columns) if columns else "*"
        sql = f"SELECT {col_expr} FROM {table.name}"
        safe_params: list[str] = list(params or [])

        if where_clause:
            sql += f" WHERE {where_clause}"
        if order_by:
            sql += f" ORDER BY {order_by}"
        if limit is not None:
            sql += f" LIMIT {limit}"

        return sql, safe_params

    @classmethod
    def aggregate(
        cls,
        table: D1Table,
        expressions: list[str],
        *,
        where_clause: str | None = None,
        params: list[str] | None = None,
    ) -> tuple[str, list[str]]:
        """SELECT <expressions> FROM … [WHERE …]

        For aggregate / stats queries.  ``expressions`` is a list of
        raw SQL select expressions, e.g.:
            ``["COUNT(*) as total",
               "SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active"]``
        """
        expr_block = ",\n    ".join(expressions)
        sql = f"SELECT\n    {expr_block}\nFROM {table.name}"
        safe_params: list[str] = list(params or [])

        if where_clause:
            sql += f"\nWHERE {where_clause}"

        return sql, safe_params

    @classmethod
    def group_by(
        cls,
        table: D1Table,
        *,
        select_expr: str,
        group_by: str,
        where_clause: str | None = None,
        params: list[str] | None = None,
        order_by: str | None = None,
        limit: int | None = None,
    ) -> tuple[str, list[str]]:
        """SELECT <select_expr> FROM … [WHERE …] GROUP BY … [ORDER BY …] [LIMIT …]

        For breakdown / timeline queries, e.g.:
            ``select_expr="event_type, COUNT(*) as count"``
            ``group_by="event_type"``
        """
        sql = f"SELECT {select_expr} FROM {table.name}"
        safe_params: list[str] = list(params or [])

        if where_clause:
            sql += f" WHERE {where_clause}"
        sql += f" GROUP BY {group_by}"
        if order_by:
            sql += f" ORDER BY {order_by}"
        if limit is not None:
            sql += f" LIMIT {limit}"

        return sql, safe_params

    # ── Internal ──────────────────────────────────────────────────────────────

    @classmethod
    def _extract(cls, table: D1Table, data: Any) -> list[str]:
        """Pull values for all table columns from data in declaration order.

        Supports Pydantic models, dataclasses, and plain dicts.
        Returns list[str] — D1 params are always strings.
        None → empty string.
        """
        if hasattr(data, "model_dump"):
            raw = data.model_dump()
        elif hasattr(data, "__dict__"):
            raw = data.__dict__
        else:
            raw = dict(data)

        result = []
        for col in table.column_names:
            val = raw[col]
            result.append("" if val is None else str(val))
        return result


__all__ = ["D1Column", "D1Index", "D1Table", "D1Q"]

