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
import os
import sys

logger = logging.getLogger(__name__)

_connected: bool = False


def _is_running_tests() -> bool:
    """Detect any common test-runner invocation.

    Catches:
      * ``manage.py test`` / ``django-admin test``
      * ``pytest`` / ``py.test`` / ``python -m pytest``
        (sets ``PYTEST_CURRENT_TEST`` while running, ``PYTEST_VERSION``
        when imported — both are reliable signals).
      * Explicit ``IS_TEST=true`` / ``DJANGO_TEST=true`` env override
        for unusual CI shapes (tox, nox, custom wrappers).

    Kept as a private helper so the conditions are documented in one
    place; callers that need this check can import it.
    """
    # 1. Explicit env override — highest signal, lets users opt in even
    #    when their runner doesn't match a known pattern.
    for key in ("IS_TEST", "DJANGO_TEST", "PYTEST_CURRENT_TEST", "PYTEST_VERSION"):
        if os.environ.get(key, "").strip().lower() not in ("", "0", "false", "no"):
            return True

    # 2. argv-based detection — handles ``manage.py test`` and the
    #    pytest entry-points (``pytest``, ``py.test``, ``python -m pytest``).
    if not sys.argv:
        return False
    argv0 = os.path.basename(sys.argv[0]).lower()
    if argv0 in ("pytest", "py.test"):
        return True
    if argv0 == "manage.py" and len(sys.argv) > 1 and sys.argv[1] == "test":
        return True
    # ``python -m pytest …`` → argv[0] is the path to pytest's __main__,
    # but ``pytest`` module is already loaded — second-cheapest check.
    if "pytest" in sys.modules:
        return True

    return False


def connect_capture() -> None:
    """Register all capture hooks. Idempotent — safe to call multiple times.

    Skipped when a test runner is detected (manage.py test, pytest,
    or explicit ``IS_TEST=true``) so test failures don't ship to
    D1/Telegram.
    """
    global _connected
    if _connected:
        return

    if _is_running_tests():
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
