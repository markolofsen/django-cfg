"""Charts service for Streamlit admin.

Provides chart data: activity, registrations, tracker.
"""

from dataclasses import dataclass

from services.base import BaseService


@dataclass
class ChartData:
    """Chart.js compatible data structure."""

    labels: list[str]
    datasets: list[dict]


@dataclass
class RecentUser:
    """Recent user info."""

    id: int
    username: str
    email: str
    date_joined: str
    is_active: bool
    last_login: str | None = None


@dataclass
class ActivityDay:
    """Activity tracker day."""

    date: str
    count: int
    level: int
    color: str
    tooltip: str


class ChartsService(BaseService):
    """Charts data service."""

    def get_activity_chart(self, days: int = 30) -> ChartData | None:
        """Get user activity chart data."""

        def fetch() -> ChartData:
            data = self.api.cfg_dashboard_charts.dashboard_api_charts_activity_retrieve(days=days)
            return ChartData(
                labels=data.labels,
                datasets=[
                    {
                        "label": ds.label,
                        "data": ds.data,
                        "backgroundColor": ds.backgroundColor,
                        "borderColor": ds.borderColor,
                        "tension": ds.tension,
                        "fill": ds.fill,
                    }
                    for ds in data.datasets
                ],
            )

        return self._safe_call("activity_chart", fetch, None)

    def get_registrations_chart(self, days: int = 30) -> ChartData | None:
        """Get user registrations chart data."""

        def fetch() -> ChartData:
            data = self.api.cfg_dashboard_charts.dashboard_api_charts_registrations_retrieve(days=days)
            return ChartData(
                labels=data.labels,
                datasets=[
                    {
                        "label": ds.label,
                        "data": ds.data,
                        "backgroundColor": ds.backgroundColor,
                        "borderColor": ds.borderColor,
                        "tension": ds.tension,
                        "fill": ds.fill,
                    }
                    for ds in data.datasets
                ],
            )

        return self._safe_call("registrations_chart", fetch, None)

    def get_recent_users(self, limit: int = 10) -> list[RecentUser]:
        """Get recently registered users."""

        def fetch() -> list[RecentUser]:
            users = self.api.cfg_dashboard_charts.dashboard_api_charts_recent_users_list(limit=limit)
            return [
                RecentUser(
                    id=u.id,
                    username=u.username,
                    email=u.email,
                    date_joined=u.date_joined,
                    is_active=u.is_active,
                    last_login=u.last_login,
                )
                for u in users
            ]

        return self._safe_call("recent_users", fetch, [])

    def get_activity_tracker(self, weeks: int = 12) -> list[ActivityDay]:
        """Get activity tracker data (GitHub-style contribution graph)."""

        def fetch() -> list[ActivityDay]:
            days = self.api.cfg_dashboard_charts.dashboard_api_charts_tracker_list(weeks=weeks)
            return [
                ActivityDay(
                    date=str(d.date),
                    count=d.count,
                    level=d.level,
                    color=d.color,
                    tooltip=d.tooltip,
                )
                for d in days
            ]

        return self._safe_call("activity_tracker", fetch, [])
