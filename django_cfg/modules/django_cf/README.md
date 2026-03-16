# django_cf

Cloudflare integration module for django-cfg. Syncs Django users and project metadata to Cloudflare D1 (SQLite at edge) automatically via post-save signals and RQ tasks.

## Module Structure

```
django_cf/
├── __init__.py          # Public API: CloudflareConfig, is_ready(), get_service()
├── __cfg__.py           # CloudflareConfig Pydantic settings
├── apps.py              # DjangoCfConfig AppConfig
├── exceptions.py        # CloudflareError, CloudflareConfigError, CloudflareQueryError, CloudflareSchemaError
├── core/
│   ├── __init__.py      # Re-exports: BaseD1Service, CloudflareD1Client, D1QueryResult, D1Q, D1Column, D1Index, D1Table
│   ├── client.py        # CloudflareD1Client — thin wrapper around official cloudflare SDK
│   ├── d1_query.py      # D1Q SQL factory — single source of truth for all D1 DML/DDL
│   ├── service.py       # BaseD1Service — abstract base for all D1-backed services
│   └── types.py         # D1QueryResult — typed SDK response wrapper
└── users/
    ├── schema.py        # PROJECTS_TABLE, USERS_TABLE, USERS_SCHEMA_STATEMENTS (via D1Q)
    ├── service.py       # UserSyncService — push_user(), full_sync_users()
    ├── signals.py       # post_save signal → RQ task
    ├── tasks.py         # sync_user_to_d1 RQ task
    └── types.py         # ProjectSyncData, UserSyncData Pydantic models
```

## Key Concepts

**D1 is SQLite-over-HTTP.** `CloudflareD1Client` wraps the official `cloudflare` Python SDK (`_sdk.d1.database.query(...)`) — synchronous, HTTP-based, not a standard DB driver connection.

**`D1Q` is the SQL factory.** Define a table once with `D1Table` (columns, PK, indexes, conflict strategy), then call `D1Q.upsert(TABLE, data)` to get `(sql, params)`. No raw SQL strings anywhere in the codebase.

**`BaseD1Service`** provides `_get_client()`, `_get_api_url()`, and `_ensure_schema()`. Subclasses implement `_get_schema_statements()`.

**User sync flow:** `post_save` signal → `sync_user_to_d1` RQ task → `UserSyncService.push_user()` → `D1Q.upsert(USERS_TABLE, data)` → D1.

**`full_sync_users()`** bulk-upserts all Django users in configurable batches (default 500).

## Configuration

```python
from django_cfg.modules.django_cf import CloudflareConfig

class MyConfig(DjangoConfig):
    cloudflare: CloudflareConfig = CloudflareConfig(
        enabled=True,
        account_id="${CF_ACCOUNT_ID}",
        api_token="${CF_API_TOKEN}",
        d1_database_id="${CF_D1_DATABASE_ID}",
        sync_server_events=True,
        sync_frontend_events=False,
        telegram_alerts_enabled=False,
        telegram_batch_interval_sec=60,   # seconds between batched flushes
        telegram_alert_on_new=True,       # flush immediately on new fingerprint
    )
```

`telegram_alerts_enabled` controls Telegram notifications for critical events. Alerts are batched — multiple occurrences of the same fingerprint are collapsed into one message.

## Public API

```python
from django_cfg.modules.django_cf import is_ready, get_service, CloudflareConfig
from django_cfg.modules.django_cf.core import D1Q, D1Column, D1Index, D1Table, BaseD1Service
```

## Extending with D1Q

To define new D1-backed tables in other modules:

```python
from django_cfg.modules.django_cf.core.d1_query import D1Column, D1Index, D1Q, D1Table

MY_TABLE = D1Table(
    name="my_records",
    columns=[
        D1Column("id",         "TEXT", primary_key=True),
        D1Column("api_url",    "TEXT", not_null=True),
        D1Column("data",       "TEXT", not_null=True, default="''"),
        D1Column("created_at", "TEXT", not_null=True),
    ],
    pk=["id", "api_url"],
    upsert_update=["data"],
)

# DDL
create_sql = D1Q.create_table(MY_TABLE)
index_sqls = D1Q.create_indexes(MY_TABLE)

# DML — single row
sql, params = D1Q.upsert(MY_TABLE, my_pydantic_model)
sql, params = D1Q.insert_ignore(MY_TABLE, my_pydantic_model)
sql, params = D1Q.upsert_increment(MY_TABLE, my_pydantic_model, increment_col="count")
sql, params = D1Q.delete_where(MY_TABLE, {"api_url": url, "is_resolved": "1"})

# DML — batch (multi-row VALUES in one SQL → one HTTP request)
sql, params = D1Q.upsert_increment_batch(MY_TABLE, list_of_models, increment_col="count")
```

## Cleanup / Delete

`CloudflareD1Client` exposes high-level cleanup methods — no raw SQL strings needed in calling code:

```python
client = get_service()._get_client()

# Delete rows matching a condition (e.g. TTL cleanup)
client.delete(MY_TABLE, "last_seen < datetime('now', ? || ' days')", ["-30"])

# Delete rows matching multiple conditions
client.delete(MY_TABLE, "is_resolved = 1 AND last_seen < datetime('now', ? || ' days')", ["-90"])

# Truncate entire table
client.truncate(MY_TABLE)
```

Both methods use `D1Q.delete_where_raw` internally and go through the same typed error handling as `execute()`.

Subclass `BaseD1Service` and implement `_get_schema_statements()` to wire DDL auto-migration on first use.

## Errors

All exceptions inherit from `CloudflareError`.

| Exception | When |
|---|---|
| `CloudflareConfigError` | Credentials missing or invalid |
| `CloudflareQueryError` | D1 HTTP request failed |
| `CloudflareSchemaError` | DDL migration failed |
