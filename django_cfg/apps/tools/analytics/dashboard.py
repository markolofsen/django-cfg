"""The analytics tab in the admin dashboard.

Self-registering: `modules/django_dashboard/resolver.py` asks every enabled
built-in app for its tabs, so a project gets the analytics tab by having
analytics enabled — which it is, by default. There is nothing to wire up.
"""

from __future__ import annotations

from django.http import HttpRequest

from django_cfg.modules.django_dashboard.models import DashboardTab

from .models import AnalyticsSite
from .services import Period, reports

TAB_SLUG = "analytics"


def get_dashboard_tabs() -> list[DashboardTab]:
    """The analytics tab — but only once there is something to show.

    Analytics is enabled by default in every django-cfg project, so an
    unconditional tab would appear for everyone, including projects that never
    send a single event. A tab whose only content is an empty state is noise.

    A site row is created automatically on the first event from a trusted domain
    (services/sites.py), so "a site exists" is exactly "traffic has arrived".
    """
    if not _has_data():
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


def _has_data() -> bool:
    """True once any site is registered.

    Runs on every dashboard render, so it must be cheap and must never raise —
    an unmigrated database (during `migrate`, or in a project that has not run
    it yet) would otherwise take the whole admin down.
    """
    from django.db import DatabaseError

    try:
        return AnalyticsSite.objects.exists()
    except DatabaseError:
        return False


def tab_context(request: HttpRequest) -> dict:
    """Data for one site over a selectable window.

    Deliberately read-time aggregation — no rollup tables, no cron. See
    services/reports.py; this is Umami's model and it holds to tens of millions
    of rows.
    """
    site = _selected_site(request)
    if site is None:
        # No site yet means no traffic has ever arrived. Say so plainly rather
        # than rendering a wall of zeros that looks like a broken install.
        return {"sites": [], "site": None, "days": 7}

    days = _selected_days(request)
    period = Period.last_days(days)

    series = reports.timeseries(site, period)
    # Bar heights are a share of the tallest day. Computed here, not in the
    # template — Django templates cannot index a dict by a variable key, and
    # adding a global `dict_get` filter to work around that would leak
    # presentation plumbing into every other app's namespace.
    peak = max((p["pageviews"] for p in series), default=0)
    for point in series:
        point["share"] = round(point["pageviews"] / peak * 100) if peak else 0

    summary = reports.summary(site, period)

    return {
        "sites": list(AnalyticsSite.objects.filter(is_active=True).order_by("domain")),
        "site": site,
        "days": days,
        "summary": summary,
        # A Django template cannot multiply, and `|floatformat:"0%"` does not
        # scale a ratio — it would render 0.5 as "0%". Do it here.
        "bounce_pct": round(summary["bounce_rate"] * 100),
        "timeseries": series,
        "top_pages": _rank(reports.top_pages(site, period, limit=10), "page", "pageviews"),
        "top_referrers": _rank(
            reports.top_referrers(site, period, limit=10), "referrer_domain", "visitors"
        ),
        "channels": _rank(reports.breakdown(site, period, "channel"), "value", "sessions"),
        "devices": _rank(reports.breakdown(site, period, "device"), "value", "sessions"),
        "browsers": _rank(reports.breakdown(site, period, "browser"), "value", "sessions"),
        "countries": _rank(reports.breakdown(site, period, "country"), "value", "sessions"),
        "online_now": reports.online_now(site),
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


def _selected_site(request: HttpRequest) -> AnalyticsSite | None:
    sites = AnalyticsSite.objects.filter(is_active=True).order_by("domain")
    requested = request.GET.get("site")
    if requested:
        site = sites.filter(domain=requested).first()
        if site is not None:
            return site
    return sites.first()


def _selected_days(request: HttpRequest) -> int:
    allowed = {1, 7, 30, 90}
    try:
        days = int(request.GET.get("days", 7))
    except (TypeError, ValueError):
        return 7
    # An allowlist, not clamping: `days` is user input and feeds a query range.
    return days if days in allowed else 7


__all__ = ["get_dashboard_tabs", "tab_context", "TAB_SLUG"]
