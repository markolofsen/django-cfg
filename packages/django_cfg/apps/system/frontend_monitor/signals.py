"""
Signal handlers for Frontend Monitor.

user_logged_in → match AnonymousSession to the authenticated User.

The session_id is read from:
  1. Cookie: fm_session_id
  2. Header: X-FM-Session-ID

Matching is done by session_id + IP double-check to avoid linking
sessions from different visitors on the same IP (e.g. offices/NAT).
"""

import logging

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone

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

        ip_address = get_client_ip(request)

        from django_cfg.apps.system.frontend_monitor.models import AnonymousSession

        # Double-check: session_id + IP must match to avoid cross-user linking
        session = AnonymousSession.objects.filter(
            session_id=session_id,
            ip_address=ip_address,
            user__isnull=True,  # Only match unlinked sessions
        ).first()

        if session:
            session.user = user
            session.matched_at = timezone.now()
            session.save(update_fields=["user", "matched_at"])
            logger.debug(
                "Frontend monitor: matched session %s to user %s",
                session_id,
                user.pk,
            )

    except Exception:
        # NEVER break the login flow
        logger.exception("Frontend monitor: error matching anonymous session on login")
