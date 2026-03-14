"""
Signal handlers for Frontend Monitor.

user_logged_in → match AnonymousSession to the authenticated User.
got_request_exception → capture server-side 500 errors into ServerEvent.

The session_id is read from:
  1. Cookie: fm_session_id
  2. Header: X-FM-Session-ID
"""

import logging
import sys

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from django_cfg.middleware.admin_notifications import get_client_ip

logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def match_anonymous_session(sender, request, user, **kwargs):
    """
    After a successful login, find the anonymous session that belongs to this
    browser and link it to the newly authenticated user.
    """
    try:
        session_id = (
            request.COOKIES.get("fm_session_id")
            or request.headers.get("X-FM-Session-ID")
        )
        if not session_id:
            return

        from django_cfg.apps.system.monitor.services.session import match_session_on_login

        match_session_on_login(
            session_id=session_id,
            ip_address=get_client_ip(request),
            user=user,
        )

    except Exception:
        # NEVER break the login flow
        logger.exception("Frontend monitor: error matching anonymous session on login")


def capture_request_exception(sender, request, **kwargs):
    """
    Capture unhandled 500 exceptions into ServerEvent.

    Connected via explicit signal.connect(dispatch_uid=...) in AppConfig.ready()
    so it is only active when server_capture_enabled=True and is not
    double-connected on repeated ready() calls in test suites.

    sender: WSGIHandler or ASGIHandler class (NOT the request object).
    request: the HttpRequest instance.

    The exception is retrieved from sys.exc_info() — Django does not pass it
    as a keyword argument; the signal fires while the exception is still active
    on the current thread.
    """
    try:
        exc_type, exc_value, tb = sys.exc_info()
        if exc_type is None:
            return

        # Skip Http404 and PermissionDenied — these are not bugs
        from django.core.exceptions import PermissionDenied
        from django.http import Http404
        if issubclass(exc_type, (Http404, PermissionDenied)):
            return

        from django_cfg.apps.system.monitor.__cfg__ import get_settings
        cfg = get_settings()
        db_alias = cfg.monitor_db_alias or "monitor"

        from django_cfg.apps.system.monitor.models.server_event import ServerEvent
        from django_cfg.apps.system.monitor.services.server_capture import ServerCaptureService

        url = ""
        http_method = ""
        try:
            url = request.get_full_path()
            http_method = request.method
        except Exception:
            pass

        ServerCaptureService().capture_exception(
            exc_type=exc_type,
            exc_value=exc_value,
            tb=tb,
            event_type=ServerEvent.EventType.SERVER_ERROR,
            db_alias=db_alias,
            url=url,
            http_method=http_method,
            http_status=500,
            logger_name="django.request",
        )

    except Exception:
        # NEVER break Django's error-handling flow
        logger.exception("ServerMonitor: failed to capture request exception")
