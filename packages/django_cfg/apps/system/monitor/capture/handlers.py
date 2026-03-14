"""
Custom logging handler for server-side error capture.

Persists ERROR/CRITICAL log records into ServerEvent via ServerCaptureService.

Safety guarantees:
1. Never raises an exception — falls back to self.handleError() → sys.stderr
2. Never imports Django models at module level (AppRegistryNotReady guard)
3. Thread-local reentrancy guard prevents infinite recursion:
   emit() → ORM fails → ORM logs ERROR → emit() called again → ...
4. ASGI-safe: detects running event loop and wraps ORM call in sync_to_async
"""

import logging
import sys
import threading

_local = threading.local()


class MonitorHandler(logging.Handler):
    """
    Logging handler that persists ERROR and CRITICAL records to ServerEvent.

    Registered on the root logger in AppConfig.ready() when
    server_capture_enabled=True.
    """

    def emit(self, record: logging.LogRecord) -> None:
        # ── Reentrancy guard ──────────────────────────────────────────────────
        # Prevents infinite loop: emit() -> ORM error -> ORM logs ERROR -> emit()
        if getattr(_local, "in_emit", False):
            return
        _local.in_emit = True
        try:
            self._do_emit(record)
        except Exception:
            self.handleError(record)  # writes to sys.stderr
        finally:
            _local.in_emit = False

    def _do_emit(self, record: logging.LogRecord) -> None:
        # ── Guard: apps must be ready ────────────────────────────────────────
        # Logging is initialized before the Django app registry. Any log record
        # that arrives during early startup would trigger AppRegistryNotReady.
        try:
            from django.apps import apps as django_apps
            if not django_apps.ready:
                return
        except Exception:
            return

        # ── Check settings ───────────────────────────────────────────────────
        try:
            from django_cfg.apps.system.monitor.__cfg__ import get_settings
            cfg = get_settings()
            if not cfg.server_capture_enabled:
                return
            db_alias = cfg.monitor_db_alias or "monitor"
            ignore_loggers = cfg.server_capture_ignore_loggers or []
        except Exception:
            db_alias = "monitor"
            ignore_loggers = []

        # Skip excluded loggers (exact match or prefix)
        if any(
            record.name == name or record.name.startswith(name + ".")
            for name in ignore_loggers
        ):
            return

        # ── Dispatch ─────────────────────────────────────────────────────────
        try:
            import asyncio
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop is not None and loop.is_running():
                from asgiref.sync import sync_to_async
                coro = sync_to_async(self._write, thread_sensitive=True)(record, db_alias)
                asyncio.ensure_future(coro, loop=loop)
            else:
                self._write(record, db_alias)
        except Exception:
            print(
                f"[MonitorHandler] Failed to dispatch record: {record.name}",
                file=sys.stderr,
            )

    @staticmethod
    def _write(record: logging.LogRecord, db_alias: str) -> None:
        try:
            from django_cfg.apps.system.monitor.services.server_capture import ServerCaptureService
            ServerCaptureService().capture_log_record(record, db_alias=db_alias)
        except Exception:
            pass
