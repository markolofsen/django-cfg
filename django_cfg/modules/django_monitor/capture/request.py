"""
django_monitor.capture.request — unhandled Django exception capture.

Hooks into got_request_exception signal → pushes UNHANDLED_EXCEPTION to D1.
"""

from __future__ import annotations

import logging
import sys

from django_cfg.modules.django_cf import is_ready

logger = logging.getLogger(__name__)


def connect_request_exception_signal() -> None:
    try:
        from django.core.signals import got_request_exception
        got_request_exception.connect(
            _on_request_exception,
            dispatch_uid="django_monitor.request_exception",
        )
    except Exception as exc:
        logger.warning("django_monitor: failed to connect request_exception signal — %s", exc)


def _on_request_exception(sender, request=None, **kwargs) -> None:
    if not is_ready():
        return

    exc_info = sys.exc_info()
    if exc_info[0] is None:
        return

    try:
        _capture_exception_to_d1(exc_info, request=request)
    except Exception as e:
        logger.debug("django_monitor: _on_request_exception suppressed — %s", e)


def _capture_exception_to_d1(exc_info, request=None) -> None:
    import hashlib
    import traceback

    exc_type, exc_value, exc_tb = exc_info
    module = getattr(exc_type, "__module__", "") or ""
    qualname = getattr(exc_type, "__qualname__", exc_type.__name__ if exc_type else "unknown")
    func_name = ""
    lineno = None

    frames = traceback.extract_tb(exc_tb)
    if frames:
        last = frames[-1]
        func_name = last.name or ""
        lineno = last.lineno

    fingerprint = hashlib.sha256(
        f"{qualname}::{module}::{func_name}".encode()
    ).hexdigest()[:16]
    stack = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    message = str(exc_value)[:2000]

    url = ""
    http_method = ""
    if request is not None:
        url = getattr(request, "path", "") or ""
        http_method = getattr(request, "method", "") or ""

    class _Event:
        pass

    ev = _Event()
    ev.fingerprint = fingerprint
    ev.event_type = "UNHANDLED_EXCEPTION"
    ev.level = "error"
    ev.message = message
    ev.stack_trace = stack[:10000]
    ev.logger_name = ""
    ev.url = url
    ev.http_method = http_method
    ev.http_status = None
    ev.func_name = func_name
    ev.module = module
    ev.lineno = lineno
    ev.extra = {}
    ev.first_seen = None
    ev.last_seen = None

    from django_cfg.modules.django_monitor import get_service
    get_service().push_server_event(ev)
