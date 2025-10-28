from __future__ import annotations

import httpx

from .models import *


class SyncCfgDashboardChartsAPI:
    """Synchronous API endpoints for Dashboard - Charts."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def dashboard_api_charts_activity_retrieve(self, days: int | None = None) -> ChartData:
        """
        Get user activity chart

        Retrieve user activity data for chart visualization
        """
        url = "/cfg/dashboard/api/charts/activity/"
        response = self._client.get(url, params={"days": days if days is not None else None})
        response.raise_for_status()
        return ChartData.model_validate(response.json())


    def dashboard_api_charts_recent_users_list(self, limit: int | None = None) -> None:
        """
        Get recent users

        Retrieve list of recently registered users
        """
        url = "/cfg/dashboard/api/charts/recent-users/"
        response = self._client.get(url, params={"limit": limit if limit is not None else None})
        response.raise_for_status()


    def dashboard_api_charts_registrations_retrieve(self, days: int | None = None) -> ChartData:
        """
        Get user registration chart

        Retrieve user registration data for chart visualization
        """
        url = "/cfg/dashboard/api/charts/registrations/"
        response = self._client.get(url, params={"days": days if days is not None else None})
        response.raise_for_status()
        return ChartData.model_validate(response.json())


    def dashboard_api_charts_tracker_list(self, weeks: int | None = None) -> None:
        """
        Get activity tracker

        Retrieve activity tracker data (GitHub-style contribution graph)
        """
        url = "/cfg/dashboard/api/charts/tracker/"
        response = self._client.get(url, params={"weeks": weeks if weeks is not None else None})
        response.raise_for_status()


