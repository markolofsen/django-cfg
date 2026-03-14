# Monitor

Full-stack error tracking and performance monitoring for Django applications.

Captures frontend (browser) events and server-side errors into a unified admin dashboard — with zero configuration required out of the box.

---

## What it does

| Capture path | What gets tracked |
|---|---|
| Browser SDK | JS errors, network failures, console logs, page views, performance |
| `got_request_exception` | Unhandled HTTP 500 errors |
| `logging.Handler` | ERROR / CRITICAL log records |
| `execute_wrapper` | Slow database queries |
| RQ `ExceptionHandler` | Failed background jobs |
| `MonitoringWorker` | OOM / SIGKILL process kills |
| `capture` API | Manual exception / message capture |

All server-side capture paths are **fire-and-forget** — they never raise and never break the calling code.

---

## Quick start

Everything is wired automatically in `AppConfig.ready()`. No configuration needed beyond installing the app.

```python
# Manual capture from application code
from django_cfg.apps.system.monitor.capture import capture

try:
    process_payment(order)
except Exception:
    capture.exception(extra={"order_id": order.id})

capture.message("Suspicious login attempt", level="warning", extra={"ip": ip})
```

---

## Architecture

```
monitor/
├── models/
│   ├── event.py          FrontendEvent — append-only browser events
│   ├── session.py        AnonymousSession — visitor → user linking
│   └── server_event.py   ServerEvent — deduplicated server errors
│
├── capture/              Server-side capture mechanisms
│   ├── api.py            CaptureClient + capture singleton (public API)
│   ├── handlers.py       MonitorHandler (logging.Handler)
│   ├── slow_query.py     execute_wrapper factory + SQL normalizer
│   └── rq.py             RQ exception handler + MonitoringWorker
│
├── services/
│   ├── ingest.py         IngestService — batch frontend event processing
│   ├── server_capture.py ServerCaptureService — exception → ServerEvent
│   ├── session.py        match_session_on_login()
│   ├── notifications.py  Telegram alerts (spike detection)
│   └── cleanup.py        CleanupService — retention policy enforcement
│
├── admin/
│   ├── event_admin.py    FrontendEventAdmin (PydanticAdmin)
│   ├── server_event_admin.py  ServerEventAdmin + resolve/reopen actions
│   └── session_admin.py  AnonymousSessionAdmin
│
├── api/
│   ├── views/ingest.py   POST /cfg/frontend-monitor/ingest/
│   └── serializers/      FrontendEventIngestSerializer
│
├── management/commands/
│   └── monitor_cleanup.py  Retention cleanup command
│
├── signals.py            user_logged_in + got_request_exception handlers
├── apps.py               AppConfig — wires all capture hooks in ready()
└── __cfg__.py            get_settings() → FrontendMonitorConfig
```

---

## Models

### `FrontendEvent`

Append-only record of a single browser-side event. Every occurrence is a new row.

Key fields: `event_type`, `level`, `message`, `stack_trace`, `url`, `fingerprint`, `session`, `user`, `ip_address`, `user_agent`, `project_name`, `environment`.

### `AnonymousSession`

Tracks a browser session by a UUID generated client-side (stored in `localStorage` / cookie `fm_session_id`). On login, the session is linked to the authenticated user.

Matching uses `session_id + IP` double-check to prevent cross-user linking behind shared NAT.

### `ServerEvent`

Deduplicated server-side error. Uses upsert semantics: one row per unique `(exception_type, module, func_name)` combination. Repeated occurrences increment `occurrence_count` and update `last_seen`.

```
fingerprint = sha256("{exception_type}::{module}::{func_name}")[:16]
```

Line numbers are **excluded from the fingerprint** — the same bug deduplicates across refactors and deploys.

**Event types:**

| Value | Capture mechanism |
|---|---|
| `SERVER_ERROR` | `got_request_exception` signal (HTTP 500) |
| `UNHANDLED_EXCEPTION` | `MonitorHandler` (logging) |
| `SLOW_QUERY` | `execute_wrapper` |
| `RQ_FAILURE` | Global RQ `ExceptionHandler` |
| `OOM_KILL` | `MonitoringWorker.work_horse_killed_handler` |
| `LOG_ERROR` | `MonitorHandler` (non-exception ERROR logs) |

**Resolution tracking:** `is_resolved`, `resolved_at`, `resolved_by`. If a resolved event recurs, it is automatically reopened (regression detection).

---

## Configuration

Defined in `FrontendMonitorConfig` (Pydantic model). All fields have defaults.

```python
# django_cfg config
frontend_monitor = FrontendMonitorConfig(
    server_capture_enabled=True,          # enable server-side capture
    monitor_db_alias="monitor",           # separate DB alias for ServerEvent writes
    slow_query_threshold_ms=500,          # 0 = disabled
    server_events_retention_days=90,      # resolved ServerEvents TTL
    server_capture_ignore_loggers=[],     # logger names to skip (prefix match)

    retention_days=90,                    # FrontendEvent TTL
    max_events_per_session_per_hour=200,  # rate limit per session
    telegram_alerts_enabled=False,        # Telegram spike notifications
    spike_threshold=10,                   # errors/minute to trigger alert
)
```

### Separate DB alias

`monitor_db_alias` (default `"monitor"`) is critical when `ATOMIC_REQUESTS=True`. Under that setting, the main DB connection rolls back on HTTP 500 — which would erase the ServerEvent write. Using a separate alias keeps monitor writes independent.

```python
# In your project DB config
databases = {
    "default": DatabaseConfig.from_url(...),
    "monitor": DatabaseConfig.from_url(..., conn_max_age=0),  # same Postgres, no pooling
}
```

---

## Ingest API

Browser events are submitted via HTTP POST from the frontend SDK.

```
POST /cfg/frontend-monitor/ingest/
Content-Type: application/json

{
  "events": [
    {
      "event_type": "ERROR",
      "message": "TypeError: Cannot read properties of null",
      "level": "error",
      "stack_trace": "...",
      "url": "https://example.com/dashboard",
      "session_id": "550e8400-e29b-41d4-a716-446655440000"
    }
  ]
}
```

- No authentication required
- Rate limited: 100 requests / minute per IP
- Returns `202 Accepted` on success
- Max batch size: 50 events

---

## Management command

```bash
# Delete records older than retention settings
python manage.py monitor_cleanup

# Override retention (both frontend and server)
python manage.py monitor_cleanup --days 30

# Preview without deleting
python manage.py monitor_cleanup --dry-run

# Verbose output with cutoff timestamps
python manage.py monitor_cleanup --dry-run --verbose
```

Open (unresolved) `ServerEvent` records are **never deleted**, regardless of age.

---

## Admin

Three admin views registered under the **Monitor** section:

- **Events** — `FrontendEvent` list with badge-colored types, search, filters
- **Sessions** — `AnonymousSession` list with user link status
- **Server Events** — `ServerEvent` triage dashboard

Bulk actions on Server Events: **Mark resolved** / **Mark unresolved**.

---

## Safety guarantees

| Concern | Solution |
|---|---|
| `AppRegistryNotReady` during startup | All model imports are lazy (inside functions) |
| Infinite recursion in `MonitorHandler` | Thread-local `in_emit` reentrancy guard |
| Slow query wrapper capturing itself | Thread-local `in_wrapper` reentrancy guard |
| ASGI / async context in `MonitorHandler` | `asyncio.get_running_loop()` + `sync_to_async` |
| Double registration on test suite reruns | `dispatch_uid` on all signals, attribute check on connections |
| `ATOMIC_REQUESTS` rollback on 500 | Separate `monitor_db_alias` connection |
| Broken ingest on notification failure | All `NotificationService` methods wrapped in `try/except` |

---

## Tests

```bash
python manage.py test django_cfg.apps.system.monitor.tests
```

Test layout mirrors the source structure:

```
tests/
├── models/         test_event.py, test_session.py, test_server_event.py
├── services/       test_ingest.py, test_server_capture.py, test_session.py
├── signals/        test_session_match.py
├── commands/       test_cleanup.py
├── views/          test_ingest.py
└── serializers/    test_ingest.py
```
