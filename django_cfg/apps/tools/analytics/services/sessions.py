"""Session resolution — find or open the visit a hit belongs to.

Sessions are maintained AT INSERT, not reconstructed at read time. That is what
keeps ``AnalyticsEvent.session_id`` populated (see models/event.py).

The subtlety is the session *window*. A naive "bucket time into 30-minute
slices" is wrong: two hits 5 minutes apart that straddle a slice boundary would
land in different sessions. The window must be anchored to the visitor's own
activity, so we look up their live session and extend it.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta

from django.db import IntegrityError, transaction

from ..models import AnalyticsSession
from . import identity


@dataclass(frozen=True)
class VisitorContext:
    """Everything we know about a hit, after the IP/UA have been reduced away."""

    site_id: int
    visitor: uuid.UUID
    previous_visitor: uuid.UUID
    user_id: int | None
    is_measurement: bool = True
    browser: str = ""
    os: str = ""
    device: str = "unknown"
    language: str = ""
    country: str = ""
    channel: str = ""
    referrer_domain: str = ""
    utm_source: str = ""
    utm_medium: str = ""
    utm_campaign: str = ""


def resolve_session(
    ctx: VisitorContext,
    *,
    now: datetime,
    pathname: str,
    timeout_minutes: int = 30,
) -> AnalyticsSession:
    """Return the visitor's live session, opening one if it has lapsed.

    Idle gap >= ``timeout_minutes`` ends a session. The visitor's *previous*
    salt-window id is also checked, so a midnight salt rotation does not split
    an in-flight visit in two.
    """
    cutoff = now - timedelta(minutes=timeout_minutes)

    live = (
        AnalyticsSession.objects.filter(
            site_id=ctx.site_id,
            visitor_id__in=[ctx.visitor, ctx.previous_visitor],
            last_seen_at__gte=cutoff,
        )
        .order_by("-last_seen_at")
        .first()
    )

    if live is not None:
        return live

    return _open_session(ctx, now=now, pathname=pathname)


def _open_session(
    ctx: VisitorContext,
    *,
    now: datetime,
    pathname: str,
) -> AnalyticsSession:
    """Create the session row. Idempotent under a concurrency race.

    Two simultaneous first-hits from the same visitor generate the SAME
    deterministic id, so the loser of the race hits the PK constraint rather
    than creating a duplicate. We swallow that and re-read.
    """
    sid = identity.session_id(visitor=ctx.visitor, window_start=now)

    session = AnalyticsSession(
        id=sid,
        site_id=ctx.site_id,
        visitor_id=ctx.visitor,
        user_id=ctx.user_id,
        is_measurement=ctx.is_measurement,
        started_at=now,
        last_seen_at=now,
        entry_pathname=pathname[:1024],
        exit_pathname=pathname[:1024],
        pageviews=0,
        events=0,
        is_bounce=True,
        channel=ctx.channel,
        referrer_domain=ctx.referrer_domain,
        utm_source=ctx.utm_source,
        utm_medium=ctx.utm_medium,
        utm_campaign=ctx.utm_campaign,
        browser=ctx.browser,
        os=ctx.os,
        device=ctx.device,
        language=ctx.language,
        country=ctx.country,
    )

    try:
        # Savepoint: without it, the IntegrityError would poison the enclosing
        # atomic block and every later statement in the request would fail.
        with transaction.atomic():
            session.save(force_insert=True)
    except IntegrityError:
        existing = AnalyticsSession.objects.filter(pk=sid).first()
        if existing is None:
            raise
        return existing

    return session


__all__ = ["VisitorContext", "resolve_session"]
