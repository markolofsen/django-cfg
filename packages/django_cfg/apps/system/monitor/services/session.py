"""
Session matching service.

Encapsulates the business logic for linking an AnonymousSession
to an authenticated user on login.
"""

import logging

from django.utils import timezone

logger = logging.getLogger(__name__)


def match_session_on_login(session_id: str, ip_address: str, user) -> bool:
    """
    Find the anonymous session that belongs to this browser and link it to the user.

    Double-check: session_id + IP must both match to prevent cross-user linking
    (e.g. multiple users behind the same NAT/office IP).

    Only matches unlinked sessions (user__isnull=True).

    Returns:
        True if a session was found and linked, False otherwise.
    """
    from django_cfg.apps.system.monitor.models import AnonymousSession

    session = AnonymousSession.objects.filter(
        session_id=session_id,
        ip_address=ip_address,
        user__isnull=True,
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
        return True

    return False
