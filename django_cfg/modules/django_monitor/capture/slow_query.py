"""
django_monitor.capture.slow_query — slow query detection via execute_wrapper.

Normalizes SQL before fingerprinting so the same query with different
parameter values deduplicates via D1 occurrence_count upsert.

Safety:
- Never logs SQL params (PII risk)
- Thread-local reentrancy guard prevents recursive capture
- Silent failure: wrapper never raises, never breaks the query path
"""

from __future__ import annotations

import logging
import re
import threading
import time

logger = logging.getLogger(__name__)

_SLOW_QUERY_THRESHOLD_MS: float = 2000.0  # 2 seconds

# Thread-local guard: prevents recursive capture when the D1 push
# itself triggers a DB query on the same connection
_reentrant = threading.local()


def connect_slow_query_wrapper() -> None:
    """Install execute_wrapper on the default DB connection."""
    try:
        from django.db import connection
        connection.execute_wrappers.append(_slow_query_wrapper)
    except Exception as exc:
        logger.warning("django_monitor: failed to install slow query wrapper — %s", exc)


def _normalize_sql(sql: str) -> str:
    """
    Strip literals so the same query with different values gets the same fingerprint.

    Replaces: string literals, floats, integers, %s/$N placeholders → ?
    Then collapses whitespace and uppercases.
    """
    sql = re.sub(r"'[^']*'", "?", sql)       # string literals
    sql = re.sub(r"\$\d+", "?", sql)         # $N placeholders (before integer rule)
    sql = re.sub(r"%s", "?", sql)            # %s placeholders
    sql = re.sub(r"\b\d+\.\d+\b", "?", sql)  # floats
    sql = re.sub(r"\b\d+\b", "?", sql)       # integers
    sql = re.sub(r"\s+", " ", sql).strip()
    return sql.upper()


def _slow_query_wrapper(execute, sql, params, many, context):
    if getattr(_reentrant, "in_wrapper", False):
        return execute(sql, params, many, context)

    _reentrant.in_wrapper = True
    try:
        start = time.monotonic()
        result = execute(sql, params, many, context)
        elapsed_ms = (time.monotonic() - start) * 1000
        if elapsed_ms >= _SLOW_QUERY_THRESHOLD_MS:
            try:
                _push_slow_query(sql, elapsed_ms)
            except Exception:
                pass
        return result
    finally:
        _reentrant.in_wrapper = False


def _push_slow_query(sql: str, elapsed_ms: float) -> None:
    import hashlib
    from django_cfg.modules.django_cf import is_ready

    if not is_ready():
        return

    normalized = _normalize_sql(sql)
    fingerprint = hashlib.sha256(normalized.encode()).hexdigest()[:16]

    class _Event:
        pass

    ev = _Event()
    ev.fingerprint = fingerprint
    ev.event_type = "SLOW_QUERY"
    ev.level = "warning"
    ev.message = f"Slow query ({elapsed_ms:.0f}ms): {sql[:200]}"
    ev.stack_trace = ""
    ev.logger_name = "django.db.backends"
    ev.url = ""
    ev.http_method = ""
    ev.http_status = None
    ev.func_name = ""
    ev.module = "django.db"
    ev.lineno = None
    ev.extra = {
        "elapsed_ms": round(elapsed_ms, 1),
        "normalized_sql": normalized[:500],
    }
    ev.first_seen = None
    ev.last_seen = None

    from django_cfg.modules.django_monitor import get_service
    get_service().push_server_event(ev)
