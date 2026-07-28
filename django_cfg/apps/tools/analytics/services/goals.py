"""Goal and funnel reports over the immutable analytics event stream."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from django.db.models import Count

from ..models import AnalyticsEvent, AnalyticsFunnel, AnalyticsGoal, AnalyticsProperty
from .reports import AnalyticsSource, Period


@dataclass(frozen=True)
class FunnelStepReport:
    name: str
    event_name: str
    visitors: int
    conversion_rate: float
    conversion_percent: int


def _source_filter(source: AnalyticsSource) -> dict[str, object]:
    return {"site__property": source} if isinstance(source, AnalyticsProperty) else {"site": source}


def goals(source: AnalyticsSource, period: Period) -> list[dict[str, object]]:
    """Configured goals and their distinct host-scoped visitors."""
    definitions = AnalyticsGoal.objects.filter(is_active=True, **_definition_filter(source)).order_by("name")
    event_names = [goal.event_name for goal in definitions]
    counts = {
        row["event_name"]: row["visitors"]
        for row in AnalyticsEvent.objects.filter(
            **_source_filter(source),
            ts__gte=period.start,
            ts__lt=period.end,
            event_name__in=event_names,
        )
        .values("event_name")
        .annotate(visitors=Count("visitor_id", distinct=True))
    }
    return [
        {"name": goal.name, "event_name": goal.event_name, "visitors": counts.get(goal.event_name, 0)}
        for goal in definitions
    ]


def funnel(source: AnalyticsSource, period: Period, definition: AnalyticsFunnel) -> list[FunnelStepReport]:
    """Ordered distinct-visitor conversion for one configured funnel.

    Rows stream in time order rather than loading an unbounded event range into
    memory. The identity is `(site_id, visitor_id)`: a property intentionally
    keeps anonymous browser identities host-scoped, matching the rest of
    analytics. Server-confirmed login events use the same request-derived
    identity on that host, so an auth journey remains joinable.
    """
    steps = list(definition.steps.order_by("position"))
    if not steps:
        return []

    by_event = {step.event_name: index for index, step in enumerate(steps)}
    completed = [0] * len(steps)
    current_identity: tuple[int, object] | None = None
    expected = 0
    rows = (
        AnalyticsEvent.objects.filter(
            **_source_filter(source),
            ts__gte=period.start,
            ts__lt=period.end,
            event_name__in=by_event,
        )
        .values_list("site_id", "visitor_id", "event_name")
        .order_by("site_id", "visitor_id", "ts", "id")
        .iterator(chunk_size=2_000)
    )
    for site_id, visitor_id, event_name in rows:
        identity = (site_id, visitor_id)
        if identity != current_identity:
            current_identity = identity
            expected = 0
        if expected >= len(steps) or by_event[event_name] != expected:
            continue
        expected += 1
        completed[expected] += 1

    first = completed[0]
    return [
        FunnelStepReport(
            name=step.name,
            event_name=step.event_name,
            visitors=completed[index],
            conversion_rate=round(completed[index] / first, 4) if first else 0.0,
            conversion_percent=round(completed[index] / first * 100) if first else 0,
        )
        for index, step in enumerate(steps)
    ]


def funnels(source: AnalyticsSource, period: Period, *, limit: int = 6) -> list[dict[str, object]]:
    """The bounded configured funnels suitable for one dashboard render."""
    definitions: Sequence[AnalyticsFunnel] = list(
        AnalyticsFunnel.objects.filter(is_active=True, **_definition_filter(source))
        .prefetch_related("steps")
        .order_by("name")[:limit]
    )
    return [
        {"name": definition.name, "steps": funnel(source, period, definition)}
        for definition in definitions
    ]


def _definition_filter(source: AnalyticsSource) -> dict[str, object]:
    return {"property": source} if isinstance(source, AnalyticsProperty) else {"site": source}


__all__ = ["FunnelStepReport", "funnel", "funnels", "goals"]
