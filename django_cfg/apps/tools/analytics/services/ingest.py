"""The ingest hot path: validate -> INSERT -> 202. Synchronously, in the request.

This is deliberately boring, and the plan (@dev/active/analytics/PLAN.md §0)
explains at length why every clever alternative was rejected. The short version,
measured on real durable storage:

    single INSERT + COMMIT ............................ 1.895 ms
    same, with SET LOCAL synchronous_commit = off ..... 0.098 ms
    psycopg connect() handshake ....................... 2.796 ms   <-- larger!

The connection handshake costs more than the durable write it carries. Any
design that adds a queue, a WAL file, or a drain daemon to defer a 0.1 ms write
is optimizing the wrong term. Umami (MIT) writes synchronously and has no worker;
Shynet ships CELERY_TASK_ALWAYS_EAGER = True by default, i.e. inline ingest is
the production baseline, not a shortcut.

Invariant: **ingest never raises into the caller's request.** Analytics failing
must never take a page down with it.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Iterable

from django.db import connections, router, transaction
from django.utils import timezone

from ..models import AnalyticsEvent, AnalyticsSession
from . import channels, identity, useragent
from .sessions import VisitorContext, resolve_session

logger = logging.getLogger("django_cfg.analytics")


def _enable_fast_commit(using: str) -> None:
    """Trade the last ~200ms of events on a hard crash for a ~19x faster write.

    Two constraints, both of which fail loudly-or-silently if ignored:

    1. MUST run inside a transaction. `SET LOCAL` outside a transaction block is
       a SILENT NO-OP — Postgres accepts the statement and does nothing, so a
       misplaced call looks fine and simply never takes effect.
    2. Postgres ONLY. `SET LOCAL` is not valid SQLite/MySQL syntax and raises
       OperationalError there, which would take the whole ingest down on any
       non-Postgres deployment (including the test suite).
    """
    connection = connections[using]
    if connection.vendor != "postgresql":
        return

    with connection.cursor() as cursor:
        cursor.execute("SET LOCAL synchronous_commit = off")


def ingest_batch(
    *,
    site,
    events: list[dict[str, Any]],
    ip: str,
    user_agent: str,
    user_id: int | None,
    fast_commit: bool = True,
    session_timeout_minutes: int = 30,
    salt_rotation_days: int = 1,
    is_measurement: bool = True,
    now: datetime | None = None,
) -> int:
    """Persist a batch of client events. Returns the number of rows written.

    Bots are dropped silently and counted as accepted — telling a crawler it was
    rejected just teaches its author to adjust.
    """
    if not events:
        return 0

    now = now or timezone.now()

    if useragent.looks_like_bot(user_agent):
        return 0

    browser, os_name, device = useragent.parse(user_agent)

    visitor = identity.visitor_id(
        site_id=site.id,
        ip=ip,
        user_agent=user_agent,
        now=now,
        rotation_days=salt_rotation_days,
    )
    previous_visitor = identity.previous_visitor_id(
        site_id=site.id,
        ip=ip,
        user_agent=user_agent,
        now=now,
        rotation_days=salt_rotation_days,
    )

    first = events[0]
    channel, ref_domain = channels.classify(
        referrer=first.get("referrer", "") or "",
        utm_source=first.get("utm_source", "") or "",
        utm_medium=first.get("utm_medium", "") or "",
        self_host=site.domain,
    )

    ctx = VisitorContext(
        site_id=site.id,
        visitor=visitor,
        previous_visitor=previous_visitor,
        user_id=user_id,
        is_measurement=is_measurement,
        browser=browser,
        os=os_name,
        device=device,
        language=(first.get("locale", "") or "")[:35],
        channel=channel,
        referrer_domain=ref_domain,
        utm_source=(first.get("utm_source", "") or "")[:255],
        utm_medium=(first.get("utm_medium", "") or "")[:255],
        utm_campaign=(first.get("utm_campaign", "") or "")[:255],
    )

    using = router.db_for_write(AnalyticsEvent)

    with transaction.atomic(using=using):
        if fast_commit:
            _enable_fast_commit(using)

        session = resolve_session(
            ctx,
            now=now,
            pathname=first.get("pathname", "") or "",
            timeout_minutes=session_timeout_minutes,
        )

        rows = list(_build_rows(events, site=site, session=session, ctx=ctx, now=now))
        AnalyticsEvent.objects.bulk_create(rows, batch_size=500)

        _touch_session(session, rows=rows, now=now)

    return len(rows)


def _build_rows(
    events: Iterable[dict[str, Any]],
    *,
    site,
    session: AnalyticsSession,
    ctx: VisitorContext,
    now: datetime,
) -> Iterable[AnalyticsEvent]:
    for e in events:
        # The client's clock is not trusted for ordering — it can be skewed or
        # forged. `ts` is server-assigned; the client timestamp is not kept.
        yield AnalyticsEvent(
            site=site,
            ts=now,
            visitor_id=ctx.visitor,
            session=session,
            user_id=ctx.user_id,
            is_measurement=ctx.is_measurement,
            event_name=(e.get("event_name") or "pageview")[:64],
            pathname=(e.get("pathname") or "")[:1024],
            route=(e.get("route") or "")[:1024],
            locale=(e.get("locale") or "")[:16],
            hostname=(e.get("hostname") or "")[:255],
            page_title=(e.get("page_title") or "")[:512],
            referrer_domain=ctx.referrer_domain[:255],
            channel=ctx.channel,
            utm_source=ctx.utm_source,
            utm_medium=ctx.utm_medium,
            utm_campaign=ctx.utm_campaign,
            utm_content=(e.get("utm_content") or "")[:255],
            utm_term=(e.get("utm_term") or "")[:255],
            click_id=(e.get("click_id") or "")[:255],
            click_id_param=(e.get("click_id_param") or "")[:32],
            props=e.get("props") or {},
        )


def _touch_session(
    session: AnalyticsSession,
    *,
    rows: list[AnalyticsEvent],
    now: datetime,
) -> None:
    """Roll the visit's mutable state forward.

    Uses F() so two concurrent batches from the same visitor cannot lose an
    increment to a read-modify-write race.
    """
    from django.db.models import F

    pageviews = sum(1 for r in rows if r.event_name == "pageview")
    last_path = rows[-1].pathname if rows else session.exit_pathname

    AnalyticsSession.objects.filter(pk=session.pk).update(
        last_seen_at=now,
        exit_pathname=last_path,
        events=F("events") + len(rows),
        pageviews=F("pageviews") + pageviews,
        duration_sec=_duration(session, now),
        # A visit stops being a bounce the moment it has a second pageview.
        is_bounce=(session.pageviews + pageviews) <= 1,
    )


def _duration(session: AnalyticsSession, now: datetime) -> int:
    delta = (now - session.started_at).total_seconds()
    return max(0, int(delta))


__all__ = ["ingest_batch"]
