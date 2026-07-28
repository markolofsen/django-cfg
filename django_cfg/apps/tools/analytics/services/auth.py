"""Analytics facts emitted from server-confirmed authentication transitions."""

from __future__ import annotations

from typing import Any

from django.utils import timezone

from .config import get_analytics_config
from .ingest import ingest_batch
from .sites import claimed_domain, resolve_site


def record_successful_login(*, user: Any, request: Any) -> int:
    """Persist one trusted login event, or silently drop unknown origins.

    The browser never supplies a user id: this function is called only from the
    accounts ``user_authenticated`` signal, after the framework has minted a
    token. ``Origin``/``Referer`` determine the site; they are browser-set
    forbidden headers, unlike a JSON body field.
    """
    config = get_analytics_config()
    if not config.store_user_id:
        return 0

    # Do not fall back to the API host. A missing browser origin is not enough
    # evidence to assign a product site, and authentication must still succeed.
    site = resolve_site(claimed_domain(request))
    if site is None:
        return 0

    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    ip = forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR", "")

    return ingest_batch(
        site=site,
        events=[
            {
                "event_name": "auth_login_success",
                "pathname": "/auth",
                "hostname": site.domain,
            }
        ],
        ip=ip,
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        user_id=user.pk,
        fast_commit=config.fast_commit,
        session_timeout_minutes=config.session_timeout_minutes,
        salt_rotation_days=config.salt_rotation_days,
        is_measurement=False,
        now=timezone.now(),
    )


__all__ = ["record_successful_login"]
