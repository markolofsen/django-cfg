"""
Slow query detection via Django's execute_wrapper API.

Installed via connection_created signal in AppConfig.ready() so every new
DB connection (WSGI workers, ASGI, RQ threads, management commands) is
instrumented automatically.

Safety:
- Never logs SQL params (may contain PII/passwords)
- Thread-local reentrancy guard prevents the ServerEvent ORM write itself
  from being captured as a slow query
- Silent failure: wrapper never raises, never breaks the query path
"""

import hashlib
import logging
import re
import threading
import time
import traceback
from typing import Callable

logger = logging.getLogger(__name__)

_reentrant = threading.local()


def _normalize_sql(sql: str) -> str:
    """
    Normalize SQL for fingerprinting — strip literals so the same query
    with different values produces the same fingerprint.

    Replaces:
    - String literals ('...') → ?
    - Floating point numbers   → ?
    - Integer literals          → ?
    - %s / $N placeholders     → ?
    Then collapses whitespace and uppercases.
    """
    sql = re.sub(r"'[^']*'", "?", sql)           # string literals
    sql = re.sub(r"\b\d+\.\d+\b", "?", sql)      # floats
    sql = re.sub(r"\b\d+\b", "?", sql)            # integers
    sql = re.sub(r"%s|\$\d+", "?", sql)           # placeholders
    sql = re.sub(r"\s+", " ", sql).strip()
    return sql.upper()


def make_slow_query_wrapper(threshold_ms: float, db_alias: str = "monitor") -> Callable:
    """
    Returns an execute_wrapper function for slow query detection.

    Args:
        threshold_ms: Queries slower than this (ms) are captured.
        db_alias: DB alias for ServerEvent writes (avoids ATOMIC_REQUESTS rollback).
    """

    def wrapper(execute, sql, params, many, context):
        # Reentrancy guard: prevents recursive capture when ServerEvent ORM
        # write itself triggers the wrapper on the same connection
        if getattr(_reentrant, "in_wrapper", False):
            return execute(sql, params, many, context)

        _reentrant.in_wrapper = True
        try:
            start = time.monotonic()
            result = execute(sql, params, many, context)
            duration_ms = (time.monotonic() - start) * 1000
            if duration_ms >= threshold_ms:
                try:
                    _capture_slow_query(sql, duration_ms, db_alias)
                except Exception:
                    pass
            return result
        finally:
            _reentrant.in_wrapper = False

    return wrapper


def _capture_slow_query(sql: str, duration_ms: float, db_alias: str) -> None:
    try:
        from django.apps import apps
        if not apps.ready:
            return

        from django_cfg.apps.system.monitor.models.server_event import ServerEvent

        normalized = _normalize_sql(sql)
        fingerprint = hashlib.sha256(normalized.encode()).hexdigest()[:16]

        # Get caller stack — filter to project frames only (skip site-packages)
        stack = traceback.extract_stack()
        project_frames = [
            f for f in stack
            if "site-packages" not in f.filename and "django/db" not in f.filename
        ]
        stack_trace = "".join(traceback.format_list(project_frames[-8:]))

        # Truncate SQL — statement only, never params (PII risk)
        safe_sql = sql[:2000] if len(sql) > 2000 else sql

        ServerEvent.record(
            exception_type="SLOW_QUERY",
            module="",
            func_name="",
            event_type=ServerEvent.EventType.SLOW_QUERY,
            message=f"Slow query: {duration_ms:.0f}ms",
            db_alias=db_alias,
            level=ServerEvent.Level.WARNING,
            stack_trace=stack_trace or None,
            extra={
                "sql": safe_sql,
                "duration_ms": round(duration_ms, 2),
                "normalized_sql": normalized[:500],
            },
        )
    except Exception:
        pass  # Never break the query path
