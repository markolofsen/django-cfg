"""
django_monitor.capture.log_handler — ERROR+ logging handler.

Attaches to root logger and ships ERROR/CRITICAL records to D1.
Thread-local reentrancy guard prevents recursion when httpx/httpcore
log at ERROR level during D1 API calls.
"""

from __future__ import annotations

import logging
import threading

from django_cfg.modules.django_cf import is_ready

logger = logging.getLogger(__name__)

# Thread-local flag — prevents recursive emit() during D1 API calls
_emit_local = threading.local()


def connect_logging_handler() -> None:
    try:
        handler = _MonitorLoggingHandler()
        handler.setLevel(logging.ERROR)
        logging.root.addHandler(handler)
    except Exception as exc:
        logger.warning("django_monitor: failed to attach logging handler — %s", exc)


class _MonitorLoggingHandler(logging.Handler):
    """Ships ERROR+ log records to D1. Never raises — silently suppresses."""

    def emit(self, record: logging.LogRecord) -> None:
        if not is_ready():
            return

        # Skip our own loggers to avoid obvious recursion
        if record.name.startswith("django_monitor") or record.name.startswith("django_cfg"):
            return

        # Thread-local guard: httpx/httpcore may log at ERROR during D1 HTTP calls
        if getattr(_emit_local, "in_emit", False):
            return
        _emit_local.in_emit = True
        try:
            self._push_record(record)
        except Exception:
            pass
        finally:
            _emit_local.in_emit = False

    def _push_record(self, record: logging.LogRecord) -> None:
        import hashlib
        import traceback as tb_module

        func_name = record.funcName or ""
        module = record.module or ""
        fingerprint = hashlib.sha256(
            f"LOG_ERROR::{module}::{func_name}".encode()
        ).hexdigest()[:16]

        stack = ""
        if record.exc_info:
            stack = "".join(tb_module.format_exception(*record.exc_info))[:10000]

        class _Event:
            pass

        ev = _Event()
        ev.fingerprint = fingerprint
        ev.event_type = "LOG_ERROR"
        ev.level = record.levelname.lower()
        ev.message = self.format(record)[:2000]
        ev.stack_trace = stack
        ev.logger_name = record.name[:200]
        ev.url = ""
        ev.http_method = ""
        ev.http_status = None
        ev.func_name = func_name
        ev.module = module
        ev.lineno = record.lineno
        ev.extra = {}
        ev.first_seen = None
        ev.last_seen = None

        from django_cfg.modules.django_monitor import get_service
        get_service().push_server_event(ev)
