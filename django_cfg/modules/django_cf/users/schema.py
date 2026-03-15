"""
django_cf.users.schema — D1 table definitions for projects and users.

All DDL/DML is generated via D1Q — no raw SQL strings.
"""

from __future__ import annotations

from django_cfg.modules.django_cf.core.d1_query import D1Column, D1Index, D1Q, D1Table

# ─────────────────────────────────────────────────────────────────────────────
# Table: projects
# ─────────────────────────────────────────────────────────────────────────────

PROJECTS_TABLE = D1Table(
    name="projects",
    columns=[
        D1Column("api_url",      "TEXT", not_null=True, primary_key=True),
        D1Column("project_name", "TEXT", not_null=True, default="''"),
        D1Column("environment",  "TEXT", not_null=True, default="'production'"),
        D1Column("synced_at",    "TEXT", not_null=True),
    ],
    upsert_update=["project_name", "environment", "synced_at"],
)

# ─────────────────────────────────────────────────────────────────────────────
# Table: users
# ─────────────────────────────────────────────────────────────────────────────

USERS_TABLE = D1Table(
    name="users",
    columns=[
        D1Column("id",          "TEXT",    not_null=True),
        D1Column("api_url",     "TEXT",    not_null=True),
        D1Column("email",       "TEXT",    not_null=True),
        D1Column("first_name",  "TEXT",    not_null=True, default="''"),
        D1Column("last_name",   "TEXT",    not_null=True, default="''"),
        D1Column("phone",       "TEXT",    not_null=True, default="''"),
        D1Column("company",     "TEXT",    not_null=True, default="''"),
        D1Column("position",    "TEXT",    not_null=True, default="''"),
        D1Column("avatar",      "TEXT",    not_null=True, default="''"),
        D1Column("is_active",   "INTEGER", not_null=True, default="1"),
        D1Column("date_joined", "TEXT",    not_null=True),
        D1Column("updated_at",  "TEXT",    not_null=True),
        D1Column("synced_at",   "TEXT",    not_null=True),
    ],
    pk=["id", "api_url"],
    indexes=[
        D1Index("idx_users_api_url",   ("api_url",)),
        D1Index("idx_users_email",     ("email", "api_url")),
        D1Index("idx_users_updated",   ("updated_at",)),
        D1Index("idx_users_is_active", ("is_active",)),
    ],
    upsert_update=[
        "email", "first_name", "last_name", "phone", "company",
        "position", "avatar", "is_active", "updated_at", "synced_at",
    ],
)

# ─────────────────────────────────────────────────────────────────────────────
# Schema statements (idempotent DDL)
# ─────────────────────────────────────────────────────────────────────────────

USERS_SCHEMA_STATEMENTS: list[str] = [
    D1Q.create_table(PROJECTS_TABLE),
    D1Q.create_table(USERS_TABLE),
    *D1Q.create_indexes(USERS_TABLE),
]

__all__ = [
    "PROJECTS_TABLE",
    "USERS_TABLE",
    "USERS_SCHEMA_STATEMENTS",
]
