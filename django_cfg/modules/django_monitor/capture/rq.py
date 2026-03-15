"""
django_monitor.capture.rq — RQ job failure capture.

Injects rq_exception_handler into RQ_EXCEPTION_HANDLERS via Django settings
so every Worker process picks it up automatically at startup.

Handler signature: (job, exc_type, exc_value, traceback) -> bool
Returns True to allow fallthrough to subsequent handlers (e.g. Sentry).
"""

from __future__ import annotations

import logging

from django_cfg.modules.django_cf import is_ready

logger = logging.getLogger(__name__)

_RQ_HANDLER_PATH = "django_cfg.modules.django_monitor.capture.rq.rq_exception_handler"


def connect_rq_exception_handler() -> None:
    """Inject our handler path into RQ_EXCEPTION_HANDLERS before worker starts."""
    try:
        from django.conf import settings as django_settings

        handlers: list = list(getattr(django_settings, "RQ_EXCEPTION_HANDLERS", []))
        if _RQ_HANDLER_PATH not in handlers:
            handlers.append(_RQ_HANDLER_PATH)
            django_settings.RQ_EXCEPTION_HANDLERS = handlers

        logger.debug("django_monitor: RQ exception handler registered")
    except Exception as exc:
        logger.warning("django_monitor: failed to register RQ exception handler — %s", exc)


def rq_exception_handler(job, exc_type, exc_value, traceback) -> bool:
    """RQ exception handler — captures failed job to D1. Returns True to allow fallthrough."""
    try:
        _push_rq_failure(job, exc_type, exc_value, traceback)
    except Exception as e:
        logger.debug("django_monitor: rq_exception_handler suppressed — %s", e)
    return True


def _push_rq_failure(job, exc_type, exc_value, exc_tb) -> None:
    import hashlib
    import traceback as tb_module

    if not is_ready():
        return

    try:
        func_name = job.func_name
    except Exception:
        func_name = "<DeserializationError>"

    try:
        queue_name: str = job.origin or "default"
        job_id: str = job.id or ""
        job_description: str = job.description or ""
    except Exception:
        queue_name = "unknown"
        job_id = ""
        job_description = ""

    module = ""
    short_func = func_name
    if "." in func_name:
        parts = func_name.rsplit(".", 1)
        module, short_func = parts[0], parts[1]

    exc_qualname = getattr(exc_type, "__qualname__", exc_type.__name__ if exc_type else "unknown")
    exc_module = getattr(exc_type, "__module__", "") or ""
    fingerprint = hashlib.sha256(
        f"RQ_FAILURE::{exc_qualname}::{exc_module}::{func_name}".encode()
    ).hexdigest()[:16]

    if exc_tb is not None:
        stack = "".join(tb_module.format_exception(exc_type, exc_value, exc_tb))[:10000]
    elif exc_value is not None:
        stack = repr(exc_value)[:2000]
    else:
        stack = ""

    class _Event:
        pass

    ev = _Event()
    ev.fingerprint = fingerprint
    ev.event_type = "RQ_FAILURE"
    ev.level = "error"
    ev.message = f"[{queue_name}] {func_name}: {exc_value}"[:2000]
    ev.stack_trace = stack
    ev.logger_name = "rq.worker"
    ev.url = ""
    ev.http_method = ""
    ev.http_status = None
    ev.func_name = short_func
    ev.module = module
    ev.lineno = None
    ev.extra = {"job_id": job_id, "queue": queue_name, "description": job_description[:200]}
    ev.first_seen = None
    ev.last_seen = None

    from django_cfg.modules.django_monitor import get_service
    get_service().push_server_event(ev)
