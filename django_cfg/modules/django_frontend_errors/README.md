# django_frontend_errors

Browser errors received by `django_monitor` (`POST /cfg/monitor/ingest/`), stored one row per signature.
On by default in every project: `manage.py migrate` creates the table. To tune or opt out:

```python
from django_cfg import FrontendErrorsConfig

frontend_errors = FrontendErrorsConfig(retention_days=30, store_warnings=True)  # enabled=False opts out
```

No setting is needed. Nothing else changes for the browser: the same client posts to the same URL.

| Piece | What |
|---|---|
| Model `FrontendError` | key (`fingerprint`, `environment`, `project_name`); `count`, `first_seen`, `last_seen`; latest `url`, `message`, `stack_trace`, `browser`, `os`, `user_agent`, `session_id`, `build_id`, `extra` (4 KB) |
| Blank fingerprint | the server makes one (`srv-` + sha1 of type, 200 chars of message, URL path) |
| Stored | `JS_ERROR`, `NETWORK_ERROR`, `ERROR`, `WARNING`; level `error`, and `warning` unless `store_warnings=False`. Page views, console, info stay log-only |
| Retention | rows not seen for `retention_days` are deleted; swept at most hourly per process while events arrive, or `manage.py purge_frontend_errors [--days N] [--dry-run]` |
| Admin | stock admin, read-only; filters environment, event type, level, project, browser; search url, message, fingerprint, build id |
| MCP | `frontend_errors_top`, `frontend_errors_recent` (read-only; no session id or user agent in any payload), registered when the store is enabled and `mcp` is on |
| Failure | a store error is logged and dropped; ingest still answers 202 |

Not kept: per-occurrence history and a distinct-session count. The table is bounded by the number of distinct errors, not by traffic.
