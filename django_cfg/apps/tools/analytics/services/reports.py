"""Read-time aggregation. No rollups, no materialized views, no cron.

This is Umami's model, and it is a deliberate choice rather than a shortcut:
Umami (the most widely deployed self-hosted analytics on Postgres) has ZERO
rollup tables and aggregates 100% on read with GROUP BY over the raw event
table. At 10-50M rows/month that is fine, and it means zero moving parts.

The index set in models/event.py is what makes it work — every query here is
scoped to (one site) x (a time range), which is exactly the
`(site_id, ts, <dim>)` prefix, so the GROUP BY stays index-only.

Rollups are deferred until measured to be needed (plan Phase 4), and note that
they buy less than they appear to: **count(distinct) is not additive**, so a
daily-uniques rollup cannot be summed into a monthly figure. The most common
number on the dashboard would fall back to the raw table anyway.

Timezone handling is the one genuinely subtle thing here. Timestamps are stored
in UTC and folded into the *site's local day* at read time. Doing it the other
way — bucketing into local days at write time — makes a timezone change a data
migration, and breaks outright for +05:30/+05:45 zones.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from django.db.models import Count, F, Q
from django.db.models.functions import TruncDate
from django.utils import timezone

from ..models import AnalyticsEvent, AnalyticsSession, AnalyticsSite


@dataclass(frozen=True)
class Period:
    """A half-open time range: [start, end).

    Half-open, never BETWEEN — an inclusive upper bound double-counts the
    boundary instant in adjacent periods.
    """

    start: datetime
    end: datetime

    @classmethod
    def last_days(cls, days: int, *, now: datetime | None = None) -> "Period":
        now = now or timezone.now()
        return cls(start=now - timedelta(days=days), end=now)


def _events(site: AnalyticsSite, period: Period):
    return AnalyticsEvent.objects.filter(
        site=site, ts__gte=period.start, ts__lt=period.end
    )


def _sessions(site: AnalyticsSite, period: Period):
    return AnalyticsSession.objects.filter(
        site=site, started_at__gte=period.start, started_at__lt=period.end
    )


def summary(site: AnalyticsSite, period: Period) -> dict[str, Any]:
    """Headline numbers.

    `visitors` is an exact count(distinct), not an estimate. See the module
    docstring: HyperLogLog would buy additivity, not speed, and postgresql-hll
    is unavailable on Supabase — so it can never be a hard dependency.
    """
    events = _events(site, period)
    sessions = _sessions(site, period)

    agg = events.aggregate(
        pageviews=Count("id", filter=Q(event_name="pageview")),
        events=Count("id"),
        visitors=Count("visitor_id", distinct=True),
        # The differentiator: how much of this traffic is signed in?
        known_users=Count("user_id", distinct=True, filter=Q(user__isnull=False)),
    )

    session_agg = sessions.aggregate(
        sessions=Count("id"),
        bounces=Count("id", filter=Q(is_bounce=True)),
    )

    total_sessions = session_agg["sessions"] or 0
    bounces = session_agg["bounces"] or 0

    return {
        **agg,
        "sessions": total_sessions,
        "bounce_rate": round(bounces / total_sessions, 4) if total_sessions else 0.0,
        "views_per_session": (
            round((agg["pageviews"] or 0) / total_sessions, 2) if total_sessions else 0.0
        ),
    }


def timeseries(site: AnalyticsSite, period: Period) -> list[dict[str, Any]]:
    """Pageviews and visitors per site-local day, for EVERY day in the period.

    TruncDate with tzinfo folds the UTC timestamps into the site's local day in
    the database, which is the whole reason `ts` is stored in UTC.

    Days with no traffic are emitted as explicit zeros rather than omitted. A
    GROUP BY only returns days that have rows, so a sparse range would collapse
    into a handful of points — and a chart drawn from them silently rescales, so
    a single busy day stretches across the whole axis and reads as continuous
    traffic. The gap has to be visible as a gap.
    """
    tz = _site_tzinfo(site)

    rows = (
        _events(site, period)
        .filter(event_name="pageview")
        .annotate(day=TruncDate("ts", tzinfo=tz))
        .values("day")
        .annotate(
            pageviews=Count("id"),
            visitors=Count("visitor_id", distinct=True),
        )
        .order_by("day")
    )
    by_day = {r["day"]: r for r in rows}

    start = period.start.astimezone(tz).date()
    end = period.end.astimezone(tz).date()

    series: list[dict[str, Any]] = []
    day = start
    while day <= end:
        row = by_day.get(day)
        series.append(
            {
                "date": day,
                "pageviews": row["pageviews"] if row else 0,
                "visitors": row["visitors"] if row else 0,
            }
        )
        day += timedelta(days=1)

    return series


def top_pages(site: AnalyticsSite, period: Period, *, limit: int = 20) -> list[dict]:
    """Most-viewed pages.

    Grouped by `route` when present, falling back to `pathname`. Without the
    templated route, /en/pricing and /ru/pricing fragment into separate rows and
    the report is meaningless on a locale-prefixed site.
    """
    rows = (
        _events(site, period)
        .filter(event_name="pageview")
        .annotate(page=_coalesce_route())
        .values("page")
        .annotate(
            pageviews=Count("id"),
            visitors=Count("visitor_id", distinct=True),
        )
        .order_by("-pageviews")[:limit]
    )
    return list(rows)


def top_referrers(site: AnalyticsSite, period: Period, *, limit: int = 20) -> list[dict]:
    rows = (
        _events(site, period)
        .filter(event_name="pageview")
        .exclude(referrer_domain="")
        .values("referrer_domain", "channel")
        .annotate(
            pageviews=Count("id"),
            visitors=Count("visitor_id", distinct=True),
        )
        .order_by("-visitors")[:limit]
    )
    return list(rows)


def breakdown(site: AnalyticsSite, period: Period, dimension: str) -> list[dict]:
    """Categorical breakdown of *sessions* (not events).

    Sessions, because browser/os/device/country are properties of the visit, not
    of each hit — counting them per event would just weight them by pageview
    count.
    """
    allowed = {"channel", "browser", "os", "device", "country", "language"}
    if dimension not in allowed:
        raise ValueError(f"Unsupported dimension {dimension!r}. Allowed: {sorted(allowed)}")

    rows = (
        _sessions(site, period)
        .exclude(**{dimension: ""})
        .values(dimension)
        .annotate(sessions=Count("id"), visitors=Count("visitor_id", distinct=True))
        .order_by("-sessions")
    )
    return [{"value": r[dimension], **{k: v for k, v in r.items() if k != dimension}} for r in rows]


def online_now(site: AnalyticsSite, *, window_minutes: int = 5) -> int:
    """Distinct visitors seen in the last N minutes.

    A partial index on this window is impossible (`ERROR: functions in index
    predicate must be marked IMMUTABLE`) — but it is also unnecessary: now() is
    STABLE, evaluated once per execution, so the plain btree on `ts` gives an
    index scan. Do NOT "optimize" this to BRIN: measured 26x slower, because the
    lossy recheck discards thousands of rows to return a handful.
    """
    cutoff = timezone.now() - timedelta(minutes=window_minutes)
    return (
        AnalyticsEvent.objects.filter(site=site, ts__gte=cutoff)
        .values("visitor_id")
        .distinct()
        .count()
    )


def user_journey(site: AnalyticsSite, user_id: int, *, limit: int = 200) -> list[dict]:
    """Every hit by one authenticated user, in order.

    This is the report hosted analytics structurally cannot produce. Served by
    the partial index on (user, ts), which stays small because user_id is NULL
    for most rows.
    """
    rows = (
        AnalyticsEvent.objects.filter(site=site, user_id=user_id)
        .values("ts", "event_name", "pathname", "route", "session_id")
        .order_by("ts")[:limit]
    )
    return list(rows)


def _coalesce_route():
    """Prefer the templated route; fall back to the raw path when absent."""
    from django.db.models import Case, CharField, Value, When

    return Case(
        When(Q(route="") | Q(route__isnull=True), then=F("pathname")),
        default=F("route"),
        output_field=CharField(),
    )


def _site_tzinfo(site: AnalyticsSite):
    """The site's IANA timezone, falling back to UTC if it is unset/invalid."""
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

    try:
        return ZoneInfo(site.timezone or "UTC")
    except (ZoneInfoNotFoundError, ValueError):
        return ZoneInfo("UTC")


__all__ = [
    "Period",
    "summary",
    "timeseries",
    "top_pages",
    "top_referrers",
    "breakdown",
    "online_now",
    "user_journey",
]
