"""
Public capture API for manual server-side instrumentation.

Usage:
    from django_cfg.apps.system.monitor.capture import capture

    # Capture current exception (call from within except block)
    try:
        process_payment(order)
    except Exception:
        capture.exception(extra={"order_id": order.id})

    # Capture a specific exception object
    try:
        do_something()
    except ValueError as e:
        capture.exception(e, level="warning")

    # Capture a plain message (no exception)
    capture.message("Suspicious login attempt", level="warning", extra={"ip": ip})

All methods are fire-and-forget — they never raise exceptions. They are no-ops
when server_capture_enabled=False or when the app is not yet initialized.
"""

import logging
import sys
from typing import Any, Optional

logger = logging.getLogger(__name__)


class CaptureClient:
    """
    Singleton capture client. All methods fail silently.
    """

    def exception(
        self,
        exc: Optional[BaseException] = None,
        *,
        level: str = "error",
        extra: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Capture an exception.

        If exc is None, reads from sys.exc_info() — call from within an except block.
        If exc is provided, uses that exception and its __traceback__.
        """
        try:
            if not self._is_ready():
                return

            if exc is None:
                exc_type, exc_value, tb = sys.exc_info()
                if exc_type is None:
                    return
            else:
                exc_type = type(exc)
                exc_value = exc
                tb = exc.__traceback__

            from django_cfg.apps.system.monitor.__cfg__ import get_settings
            cfg = get_settings()
            if not cfg.server_capture_enabled:
                return

            from django_cfg.apps.system.monitor.models.server_event import ServerEvent
            from django_cfg.apps.system.monitor.services.server_capture import ServerCaptureService

            ServerCaptureService().capture_exception(
                exc_type=exc_type,
                exc_value=exc_value,
                tb=tb,
                event_type=ServerEvent.EventType.UNHANDLED_EXCEPTION,
                db_alias=cfg.monitor_db_alias or "monitor",
                extra=extra or {},
            )
        except Exception:
            pass

    def message(
        self,
        msg: str,
        *,
        level: str = "info",
        extra: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Capture a plain message (no exception).
        """
        try:
            if not self._is_ready():
                return

            from django_cfg.apps.system.monitor.__cfg__ import get_settings
            cfg = get_settings()
            if not cfg.server_capture_enabled:
                return

            from django_cfg.apps.system.monitor.models.server_event import ServerEvent

            ServerEvent.record(
                exception_type="MESSAGE",
                module="",
                func_name="",
                event_type=ServerEvent.EventType.LOG_ERROR,
                message=msg[:2000],
                db_alias=cfg.monitor_db_alias or "monitor",
                level=level,
                extra=extra or {},
            )
        except Exception:
            pass

    @staticmethod
    def _is_ready() -> bool:
        try:
            from django.apps import apps
            return apps.ready
        except Exception:
            return False


# Module-level singleton — the public API
capture = CaptureClient()
