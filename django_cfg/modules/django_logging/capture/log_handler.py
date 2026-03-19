"""D1LogHandler — push log records to Cloudflare D1.

Thread-safe, non-blocking, reentrant-safe.
"""

from __future__ import annotations

import logging
import threading
import traceback
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.service import LogSyncService


class D1LogHandler(logging.Handler):
    """Logging handler that pushes records to D1.

    - Reentrancy guard prevents infinite recursion (D1 client uses httpx which logs at ERROR)
    - Non-blocking: each push runs in a daemon thread
    - Never raises — logging must never crash the app
    """

    _local = threading.local()

    def __init__(
        self,
        service: "LogSyncService",
        min_level: int = logging.WARNING,
        normalize: bool = True,
    ):
        super().__init__(level=min_level)
        self._service = service
        self._normalize = normalize

    def emit(self, record: logging.LogRecord) -> None:
        # Level check (in case emit is called directly, bypassing framework filter)
        if record.levelno < self.level:
            return

        # Reentrancy guard
        if getattr(self._local, "in_emit", False):
            return

        # Skip records already captured by django_monitor
        if getattr(record, "_monitor_captured", False):
            return

        self._local.in_emit = True
        try:
            self._push(record)
        except Exception:
            pass
        finally:
            self._local.in_emit = False

    def _push(self, record: logging.LogRecord) -> None:
        from ..core.fingerprint import make_fingerprint
        from ..core.types import LogEventSyncData

        now = datetime.now(timezone.utc).isoformat()
        msg = record.getMessage()

        # Build stack trace from exception info
        stack = ""
        if record.exc_info and record.exc_info[2] is not None:
            stack = "".join(traceback.format_exception(*record.exc_info))

        data = LogEventSyncData(
            fingerprint=make_fingerprint(
                record.levelname, record.name, msg, normalize=self._normalize,
            ),
            api_url=self._service._get_api_url(),
            level=record.levelname.lower(),
            logger_name=record.name,
            message=msg[:5000],
            module=getattr(record, "module", "") or "",
            func_name=getattr(record, "funcName", "") or "",
            pathname=getattr(record, "pathname", "") or "",
            lineno=getattr(record, "lineno", 0),
            stack_trace=stack[:10000],
            extra="{}",
            first_seen=now,
            last_seen=now,
        )

        # Non-blocking push via daemon thread
        t = threading.Thread(
            target=self._safe_push,
            args=(data,),
            daemon=True,
        )
        t.start()

    def _safe_push(self, data) -> None:
        """Push in background thread — never raises."""
        try:
            self._service.push_log_event(data)
        except Exception:
            pass


__all__ = ["D1LogHandler"]
