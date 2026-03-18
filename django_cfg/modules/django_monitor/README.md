# django_monitor

Server-side error tracking and monitoring module for django-cfg. Captures exceptions, slow queries, RQ job failures, and ERROR-level log records. Pushes events to Cloudflare D1 via `django_cf`. No PostgreSQL required.

## Module Structure

```
django_monitor/
├── __init__.py              # Public API: get_service(), capture_exception(), capture_message()
├── apps.py                  # DjangoMonitorConfig AppConfig — auto-connects capture hooks
├── exceptions.py            # MonitorError, MonitorConfigError, MonitorSyncError
├── capture/
│   ├── __init__.py          # connect_capture() — wires all 4 hooks at once
│   ├── request.py           # got_request_exception signal → UNHANDLED_EXCEPTION
│   ├── log_handler.py       # ERROR/CRITICAL logging.Handler → LOG_ERROR (thread-local reentrancy guard)
│   ├── slow_query.py        # execute_wrapper → SLOW_QUERY (SQL normalization for dedup)
│   ├── rq.py                # RQ exception handler → RQ_FAILURE (injected via RQ_EXCEPTION_HANDLERS)
│   └── notify.py            # Telegram alert routing (after successful D1 push)
├── events/
│   ├── schema.py            # SERVER_EVENTS_TABLE, FRONTEND_EVENTS_TABLE, MONITOR_SCHEMA_STATEMENTS (via D1Q)
│   ├── service.py           # MonitorSyncService — push_server_event(), push_frontend_event()
│   ├── tasks.py             # cleanup_d1_events() RQ task
│   └── types.py             # ServerEventSyncData, FrontendEventSyncData Pydantic models
└── streamlit/
    ├── pages/
    │   ├── server_events.py  # Streamlit admin page — server errors dashboard
    │   └── frontend_events.py # Streamlit admin page — browser events dashboard
    └── services/
        └── d1_query.py      # D1 read queries for Streamlit pages
```

## Capture Paths

All capture paths are fire-and-forget — they never raise, never break the calling code.

| Source | Event type | Module |
|---|---|---|
| `got_request_exception` signal | `UNHANDLED_EXCEPTION` | `capture/request.py` |
| `logging.Handler` (ERROR+) | `LOG_ERROR` | `capture/log_handler.py` |
| `execute_wrapper` (slow queries) | `SLOW_QUERY` | `capture/slow_query.py` |
| RQ `exception_handler` | `RQ_FAILURE` | `capture/rq.py` |
| `capture_exception()` | `UNHANDLED_EXCEPTION` | `__init__.py` |
| `capture_message()` | configurable level | `__init__.py` |

## Key Concepts

**Requires `django_cf`.** If `django_cf` is not configured and ready (`is_ready()` returns `False`), all capture is a no-op.

**Server events use upsert-increment.** The same error (same fingerprint = `sha256[:16]` of `exc_type::module::func`) increments `occurrence_count` and resets `is_resolved=0`, enabling regression detection.

**Frontend events use upsert-increment.** Same fingerprint (= `sha256[:64]` — client-generated or server-side fallback) increments `occurrence_count` and updates `last_seen`. Events without a client fingerprint (`NETWORK_ERROR`, zod validation) get a server-side sha256 fallback. `PAGE_VIEW` / `PERFORMANCE` get a UUID fingerprint → always append-only.

**SQL normalization in slow query capture.** Literals and numbers are replaced with `?` before fingerprinting so `WHERE id = 1` and `WHERE id = 2` map to the same event.

**Thread-local reentrancy guard in `log_handler.py`.** Prevents infinite recursion when httpx (used by the D1 HTTP client) logs at ERROR level during D1 API calls.

**Telegram notifications via `notify.py`.** Batched: events accumulate in `_AlertBatch` (in-memory, thread-safe), flushed every `telegram_batch_interval_sec` seconds (default 60s). New fingerprints flush immediately when `telegram_alert_on_new=True`. Controlled by `CloudflareConfig.telegram_alerts_enabled`.

**RQ exception handler returns `True`** to allow fallthrough to subsequent handlers (e.g. Sentry).

**Slow query thresholds:** capture at 2000ms, Telegram alert at 5000ms.

## Setup

`AppConfig.ready()` calls `connect_capture()` automatically — no manual wiring required:

```python
# Happens automatically in DjangoMonitorConfig.ready():
from django_cfg.modules.django_monitor.capture import connect_capture
connect_capture()
```

## Manual Capture

```python
from django_cfg.modules.django_monitor import capture_exception, capture_message

try:
    process_payment(order)
except Exception as exc:
    capture_exception(exc, url=request.path, http_method=request.method)

capture_message("Suspicious login attempt", level="warning", extra={"ip": ip})
```

## Event Types

`UNHANDLED_EXCEPTION`, `SERVER_ERROR`, `LOG_ERROR`, `SLOW_QUERY`, `RQ_FAILURE`

## Cleanup

`cleanup_d1_events()` is an RQ task that removes resolved server events older than N days and trims old frontend events. Internally uses `client.delete(TABLE, where_clause, params)` from `CloudflareD1Client` — no raw SQL strings in task code.

Schedule via `RQScheduleConfig` in your config:

```python
from django_cfg.modules.django_monitor.events.tasks import cleanup_d1_events

RQScheduleConfig(
    func="django_cfg.modules.django_monitor.events.tasks.cleanup_d1_events",
    cron="0 3 * * *",   # daily at 3am
    kwargs={"server_events_days": 90, "frontend_events_days": 30},
    description="Trim old D1 monitor events",
)
```

## Querying Events via CLI

Query `server_events` and `frontend_events` from the terminal using `d1_logs` (a `django_cf` management command):

```bash
uv run python manage.py d1_logs server_events --level error --since 1h
uv run python manage.py d1_logs frontend_events --search "TypeError"
```

See the [django_cf d1-logs guide](../django_cf/@docs/d1-logs.md) for all options.

## Errors

| Exception | When |
|---|---|
| `MonitorConfigError` | `api_url` or credentials not configured |
| `MonitorSyncError` | D1 push failed |
