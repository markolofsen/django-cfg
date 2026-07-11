"""
django_monitor.capture.log_handler — ERROR+ logging handler.

Attaches to root logger and captures ERROR/CRITICAL records.
Thread-local reentrancy guard prevents recursion when transports
(httpx, telegram) log at ERROR level during alert delivery.
"""

from __future__ import annotations

import logging
import threading

logger = logging.getLogger(__name__)

# Thread-local flag — prevents recursive emit() during alert delivery
_emit_local = threading.local()


def connect_logging_handler() -> None:
    try:
        handler = _MonitorLoggingHandler()
        handler.setLevel(logging.ERROR)
        logging.root.addHandler(handler)
    except Exception as exc:
        logger.warning("django_monitor: failed to attach logging handler — %s", exc)


class _MonitorLoggingHandler(logging.Handler):
    """Captures ERROR+ log records. Never raises — silently suppresses."""

    def emit(self, record: logging.LogRecord) -> None:
        from django_cfg.modules.django_monitor import is_enabled
        if not is_enabled():
            return

        # Skip our own loggers to avoid obvious recursion
        if record.name.startswith("django_monitor") or record.name.startswith("django_cfg"):
            return

        # Thread-local guard: transports may log at ERROR during alert delivery
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

        from django_cfg.modules.django_monitor import capture_server_event
        capture_server_event(ev)
