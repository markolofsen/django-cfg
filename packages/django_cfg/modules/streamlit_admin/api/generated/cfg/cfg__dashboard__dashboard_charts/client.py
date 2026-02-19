from __future__ import annotations

import httpx

from .models import (
    ActivityTrackerDay,
    ChartData,
    RecentUser,
)


class CfgDashboardChartsAPI:
    """API endpoints for Dashboard - Charts."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def dashboard_api_charts_activity_retrieve(
        self,
        days: int | None = None,
    ) -> ChartData:
        """
        Get user activity chart

        Retrieve user activity data for chart visualization
        """
        url = "/cfg/dashboard/api/charts/activity/"
        _params = {
            k: v for k, v in {
                "days": days,
            }.items() if v is not None
        }
        response = await self._client.get(url, params=_params)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return ChartData.model_validate(response.json())


    async def dashboard_api_charts_recent_users_list(
        self,
        limit: int | None = None,
        ordering: str | None = None,
        search: str | None = None,
    ) -> list[RecentUser]:
        """
        Get recent users

        Retrieve list of recently registered users
        """
        url = "/cfg/dashboard/api/charts/recent-users/"
        _params = {
            k: v for k, v in {
                "limit": limit,
                "ordering": ordering,
                "search": search,
            }.items() if v is not None
        }
        response = await self._client.get(url, params=_params)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return [RecentUser.model_validate(item) for item in response.json()]


    async def dashboard_api_charts_registrations_retrieve(
        self,
        days: int | None = None,
    ) -> ChartData:
        """
        Get user registration chart

        Retrieve user registration data for chart visualization
        """
        url = "/cfg/dashboard/api/charts/registrations/"
        _params = {
            k: v for k, v in {
                "days": days,
            }.items() if v is not None
        }
        response = await self._client.get(url, params=_params)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return ChartData.model_validate(response.json())


    async def dashboard_api_charts_tracker_list(
        self,
        ordering: str | None = None,
        search: str | None = None,
        weeks: int | None = None,
    ) -> list[ActivityTrackerDay]:
        """
        Get activity tracker

        Retrieve activity tracker data (GitHub-style contribution graph)
        """
        url = "/cfg/dashboard/api/charts/tracker/"
        _params = {
            k: v for k, v in {
                "ordering": ordering,
                "search": search,
                "weeks": weeks,
            }.items() if v is not None
        }
        response = await self._client.get(url, params=_params)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return [ActivityTrackerDay.model_validate(item) for item in response.json()]


