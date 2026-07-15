# django_monitor

Error capture and Telegram alerting for django-cfg. Captures unhandled exceptions, ERROR-level log records, slow queries, RQ job failures, and browser events.

**No persistence.** There are no models, no migrations, no external database. Every captured event becomes a JSON log line (`logs/djangocfg/monitor.log`) and — when Telegram is configured — joins a batched Telegram alert. That is the whole storage story: events are **not stored and not queryable**.

## Module Structure

```
django_monitor/
├── __init__.py              # Public API: is_enabled(), capture_exception(), capture_message(),
│                            #             capture_server_event(), capture_frontend_events()
├── apps.py                  # DjangoMonitorConfig AppConfig — calls connect_capture() in ready()
├── exceptions.py            # MonitorError, MonitorConfigError, MonitorSyncError
├── urls.py                  # Router mounted at /cfg/monitor/ (OpenAPI group: cfg_monitor)
├── utils.py                 # parse_user_agent() → (browser, os, device_type)
├── capture/
│   ├── __init__.py          # connect_capture() — wires all 4 hooks; skipped under test runners
│   ├── request.py           # got_request_exception signal → UNHANDLED_EXCEPTION
│   ├── log_handler.py       # ERROR/CRITICAL logging.Handler → LOG_ERROR (thread-local guard)
│   ├── slow_query.py        # execute_wrapper → SLOW_QUERY (SQL normalization for dedup)
│   ├── rq.py                # RQ exception handler → RQ_FAILURE (via RQ_EXCEPTION_HANDLERS)
│   └── notify.py            # Batched Telegram alerts (_AlertBatch)
├── api/
│   ├── serializers.py       # FrontendEventIngestSerializer, IngestBatchSerializer
│   └── views.py             # MonitorIngestViewSet — POST /cfg/monitor/ingest/
├── services/
│   └── ingest.py            # ingest_frontend_events() — enrich + hand to capture pipeline
└── management/commands/
    └── monitor_status.py    # Alerting state + event log location
```

## Capture Paths

All capture paths are fire-and-forget — they never raise, never break the calling code.

| Source | Event type | Module |
|---|---|---|
| `got_request_exception` signal | `UNHANDLED_EXCEPTION` | `capture/request.py` |
| `logging.Handler` (ERROR+) | `LOG_ERROR` | `capture/log_handler.py` |
| `execute_wrapper` (slow queries) | `SLOW_QUERY` | `capture/slow_query.py` |
| RQ `exception_handler` | `RQ_FAILURE` | `capture/rq.py` |
| `capture_exception()` | `SERVER_ERROR` | `__init__.py` |
| `capture_message()` | `LOG_ERROR` (level is a parameter) | `__init__.py` |
| `POST /cfg/monitor/ingest/` | frontend types (`JS_ERROR`, …) | `services/ingest.py` |

## Key Concepts

**Always on, zero-config.** `is_enabled()` returns `True` unconditionally. There is no config model and no enable flag. The app is always added to `INSTALLED_APPS` (`core/builders/apps_builder.py`) and the ingest URL is always mounted.

**Two sinks per event.** `capture_server_event()` writes one JSON line via `_log_event()` (the standard django-cfg logging pipeline → `logs/djangocfg/monitor.log`, midnight rotation, 30 days) and then calls `notify_server_event()` to queue a Telegram alert. `capture_frontend_events()` does the same per event, but only `level == "error"` events join the Telegram batch (as `FRONTEND_ERROR`).

**Nothing is persisted.** No `models.py`, no `migrations/`, no rows written anywhere. `PAGE_VIEW` / `PERFORMANCE` / `CONSOLE` events are logged and dropped — there is no dashboard, no query API, no analytics.

**Fingerprints group alerts, not rows.** A fingerprint (`sha256[:16]` of `qualname::module::func`, or of the normalized SQL for slow queries) is used by the alert batcher to collapse repeats into a single alert line with a count. It does not key any table.

**SQL normalization in slow query capture.** Literals, numbers, and `%s` / `$N` placeholders are replaced with `?` before fingerprinting, so `WHERE id = 1` and `WHERE id = 2` share a fingerprint. Params are never logged (PII).

**Thread-local reentrancy guards.** `log_handler.py` and `slow_query.py` both guard against recursion (a transport logging at ERROR during alert delivery, or a query issued while capturing a query).

**Telegram batching (`notify.py`).** Events accumulate in an in-memory, thread-safe `_AlertBatch`, flushed every 60 seconds by a daemon `threading.Timer`. A fingerprint not alerted in the last 600s flushes immediately. Alerts are on exactly when `TelegramConfig` is set on `DjangoConfig` — no separate switch.

**Test-runner auto-disable.** `connect_capture()` returns early when `_is_running_tests()` detects pytest / `manage.py test` / `IS_TEST=true`, so test failures never ship to the log pipeline or Telegram.

**RQ exception handler returns `True`** to allow fallthrough to subsequent handlers (e.g. Sentry).

**Thresholds:** slow query captured at 2000ms, Telegram-alerted at 5000ms.

## Setup

Nothing to set up. `DjangoMonitorConfig.ready()` calls `connect_capture()` automatically:

```python
# Happens automatically in DjangoMonitorConfig.ready():
from django_cfg.modules.django_monitor.capture import connect_capture
connect_capture()
```

Telegram alerts turn on by themselves as soon as `TelegramConfig` is set on your `DjangoConfig`. No Telegram — no alerts, nothing to configure either way.

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

Server: `UNHANDLED_EXCEPTION`, `SERVER_ERROR`, `LOG_ERROR`, `SLOW_QUERY`, `RQ_FAILURE`
Frontend (ingest): `JS_ERROR`, `NETWORK_ERROR`, `ERROR`, `WARNING`, `PAGE_VIEW`, `PERFORMANCE`, `CONSOLE`

## Status

```bash
python manage.py monitor_status
```

Prints whether Telegram alerts are on, the path of `logs/djangocfg/monitor.log`, and its current line count / size.

## Errors

The exception hierarchy in `exceptions.py` is public API, but the capture pipeline never raises it — every `capture_*` function swallows failures.

| Exception | Meaning |
|---|---|
| `MonitorError` | Base class; carries `suggestion` and `original_error` |
| `MonitorConfigError` | The module is not configured correctly |
| `MonitorSyncError` | Pushing a captured event downstream failed |
