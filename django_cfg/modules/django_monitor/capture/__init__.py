"""
django_monitor.capture — event capture hooks.

connect_capture() registers all hooks at Django startup.

Sub-modules:
  request     — got_request_exception signal → UNHANDLED_EXCEPTION
  log_handler — root logging handler → LOG_ERROR (with reentrancy guard)
  slow_query  — DB execute_wrapper → SLOW_QUERY (with SQL normalization)
  rq          — RQ_EXCEPTION_HANDLERS injection → RQ_FAILURE
  notify      — Telegram alerts after D1 push
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_connected: bool = False


def connect_capture() -> None:
    """Register all capture hooks. Idempotent — safe to call multiple times.

    Skipped when running tests (``manage.py test``) to avoid pushing
    test events to D1/Telegram.
    """
    global _connected
    if _connected:
        return

    import sys
    if "test" in sys.argv:
        _connected = True
        return

    from .request import connect_request_exception_signal
    from .log_handler import connect_logging_handler
    from .slow_query import connect_slow_query_wrapper
    from .rq import connect_rq_exception_handler

    connect_request_exception_signal()
    connect_logging_handler()
    connect_slow_query_wrapper()
    connect_rq_exception_handler()

    _connected = True
    logger.debug("django_monitor: capture hooks connected")


# Re-export so RQ can resolve the dotted path via django_monitor.capture.rq_exception_handler
from .rq import rq_exception_handler  # noqa: E402

__all__ = [
    "connect_capture",
    "rq_exception_handler",
]
