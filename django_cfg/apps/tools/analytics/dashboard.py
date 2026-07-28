"""The analytics tab in the admin dashboard.

Self-registering: `modules/django_dashboard/resolver.py` asks every enabled
built-in app for its tabs, so a project gets the analytics tab by having
analytics enabled — which it is, by default. There is nothing to wire up.
"""

from __future__ import annotations

from urllib.parse import urlencode

from django.db import DatabaseError, transaction
from django.http import HttpRequest

from django_cfg.modules.django_dashboard.models import DashboardTab

from .models import AnalyticsProperty, AnalyticsSite
from .services import Period, ensure_property, funnels as funnel_reports, goals as goal_reports, reports

TAB_SLUG = "analytics"
REPORT_ROW_LIMIT = 50


def get_dashboard_tabs() -> list[DashboardTab]:
    """The analytics tab, once its database schema is ready.

    The tab owns a useful empty state, so it should be visible before the first
    event arrives.  It stays hidden only while migrations have not created the
    analytics tables yet.
    """
    if not _schema_ready():
        return []

    return [
        DashboardTab(
            slug=TAB_SLUG,
            title="Analytics",
            icon="analytics",
            template="analytics/dashboard_tab.html",
            callback="django_cfg.apps.tools.analytics.dashboard.tab_context",
        )
    ]


def _schema_ready() -> bool:
    """Return whether the analytics tables are queryable.

    Runs on every dashboard render, so it must be cheap and must never raise —
    an unmigrated database (during `migrate`, or in a project that has not run
    it yet) would otherwise take the whole admin down.
    """
    try:
        # Dashboard views commonly run inside ATOMIC_REQUESTS.  PostgreSQL
        # marks that whole transaction as failed after an unmigrated-table
        # error, even when DatabaseError is caught.  A nested atomic block
        # gives this probe its own savepoint so the outer request transaction
        # remains usable by extension-provided tabs.
        with transaction.atomic():
            AnalyticsSite.objects.exists()
            AnalyticsProperty.objects.exists()
    except DatabaseError:
        return False
    return True


def tab_context(request: HttpRequest) -> dict:
    """Data for one host or automatically grouped property over a time window.

    Deliberately read-time aggregation — no rollup tables, no cron. See
    services/reports.py; this is Umami's model and it holds to tens of millions
    of rows.
    """
    sites = _active_sites()
    properties = _active_properties(sites)
    source, source_kind = _selected_source(request, sites, properties)
    if source is None:
        days = _selected_days(request)
        period = Period.last_days(days)
        series = _empty_timeseries(period)
        return {
            "sites": [],
            "properties": [],
            "site": None,
            "property": None,
            "source": None,
            "source_kind": None,
            "selected_query": "",
            "days": days,
            "summary": {
                "visitors": 0,
                "pageviews": 0,
                "events": 0,
                "known_users": 0,
                "sessions": 0,
                "bounce_rate": 0.0,
                "views_per_session": 0.0,
            },
            "bounce_pct": 0,
            "timeseries": series,
            "top_pages": [],
            "top_referrers": [],
            "channels": [],
            "devices": [],
            "browsers": [],
            "countries": [],
            "online_now": 0,
            "goals": [],
            "funnels": [],
        }

    days = _selected_days(request)
    period = Period.last_days(days)

    series = reports.timeseries(source, period)
    # Bar heights are a share of the tallest day. Computed here, not in the
    # template — Django templates cannot index a dict by a variable key, and
    # adding a global `dict_get` filter to work around that would leak
    # presentation plumbing into every other app's namespace.
    peak = max((p["pageviews"] for p in series), default=0)
    for point in series:
        point["share"] = round(point["pageviews"] / peak * 100) if peak else 0

    summary = reports.summary(source, period)

    selected_query = f"{urlencode({source_kind: source.domain})}&"

    return {
        "sites": sites,
        "properties": properties,
        "site": source if isinstance(source, AnalyticsSite) else None,
        "property": source if isinstance(source, AnalyticsProperty) else None,
        "source": source,
        "source_kind": source_kind,
        "selected_query": selected_query,
        "days": days,
        "summary": summary,
        # A Django template cannot multiply, and `|floatformat:"0%"` does not
        # scale a ratio — it would render 0.5 as "0%". Do it here.
        "bounce_pct": round(summary["bounce_rate"] * 100),
        "timeseries": series,
        # Rendering an unbounded categorical breakdown makes a dashboard slow
        # and unusable on a busy site. Fifty gives operators enough long-tail
        # context to search and inspect in the tab, while keeping one response
        # and one DOM tree predictably small.
        "top_pages": _rank(
            reports.top_pages(source, period, limit=REPORT_ROW_LIMIT), "page", "pageviews"
        ),
        "top_referrers": _rank(
            reports.top_referrers(source, period, limit=REPORT_ROW_LIMIT),
            "referrer_domain",
            "visitors",
        ),
        "channels": _rank(
            reports.breakdown(source, period, "channel", limit=REPORT_ROW_LIMIT),
            "value",
            "sessions",
        ),
        "devices": _rank(
            reports.breakdown(source, period, "device", limit=REPORT_ROW_LIMIT),
            "value",
            "sessions",
        ),
        "browsers": _rank(
            reports.breakdown(source, period, "browser", limit=REPORT_ROW_LIMIT),
            "value",
            "sessions",
        ),
        "countries": _rank(
            reports.breakdown(source, period, "country", limit=REPORT_ROW_LIMIT),
            "value",
            "sessions",
        ),
        "online_now": reports.online_now(source),
        "goals": _rank(goal_reports(source, period), "name", "visitors"),
        "funnels": funnel_reports(source, period),
    }


def _rank(rows: list[dict], label_key: str, count_key: str) -> list[dict]:
    """Normalize a report into the {label, count, share} shape the table renders.

    `share` is relative to the top row, so the leader's bar is always full width.
    """
    top = rows[0][count_key] if rows else 0
    return [
        {
            "label": row.get(label_key) or "",
            "count": row[count_key],
            "share": round(row[count_key] / top * 100) if top else 0,
        }
        for row in rows
    ]


def _empty_timeseries(period: Period) -> list[dict]:
    """Zero-filled UTC series for a dashboard that has no registered site."""
    from datetime import timedelta

    day = period.start.date()
    end = period.end.date()
    rows = []
    while day <= end:
        rows.append({"date": day, "pageviews": 0, "visitors": 0, "share": 0})
        day += timedelta(days=1)
    return rows


def _active_sites() -> list[AnalyticsSite]:
    sites = list(AnalyticsSite.objects.filter(is_active=True).order_by("domain"))
    # Existing AnalyticsSite rows predate properties. Attach them lazily on the
    # first dashboard read so no data migration needs deployment-specific
    # security-domain settings.
    return [ensure_property(site) for site in sites]


def _active_properties(sites: list[AnalyticsSite]) -> list[AnalyticsProperty]:
    ids = {site.property_id for site in sites if site.property_id}
    return list(
        AnalyticsProperty.objects.filter(pk__in=ids, is_active=True).order_by("domain")
    )


def _selected_source(
    request: HttpRequest,
    sites: list[AnalyticsSite],
    properties: list[AnalyticsProperty],
) -> tuple[AnalyticsSite | AnalyticsProperty | None, str | None]:
    requested_property = request.GET.get("property")
    if requested_property:
        for property_ in properties:
            if property_.domain == requested_property:
                return property_, "property"

    requested_site = request.GET.get("site")
    if requested_site:
        for site in sites:
            if site.domain == requested_site:
                return site, "site"

    # Prefer a real multi-host property. A one-host deployment keeps the
    # historic dashboard default unchanged, while cmdop.com + my.cmdop.com
    # becomes an aggregate as soon as both hosts have traffic.
    property_site_counts = {
        property_.pk: sum(site.property_id == property_.pk for site in sites)
        for property_ in properties
    }
    for property_ in properties:
        if property_site_counts[property_.pk] > 1:
            return property_, "property"
    if sites:
        return sites[0], "site"
    return None, None


def _selected_days(request: HttpRequest) -> int:
    allowed = {1, 7, 30, 90}
    try:
        days = int(request.GET.get("days", 7))
    except (TypeError, ValueError):
        return 7
    # An allowlist, not clamping: `days` is user input and feeds a query range.
    return days if days in allowed else 7


__all__ = ["get_dashboard_tabs", "tab_context", "TAB_SLUG"]
