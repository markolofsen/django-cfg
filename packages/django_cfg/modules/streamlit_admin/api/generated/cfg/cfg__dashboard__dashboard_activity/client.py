from __future__ import annotations

import httpx

from .models import (
    ActivityEntry,
    QuickAction,
)


class CfgDashboardActivityAPI:
    """API endpoints for Dashboard - Activity."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def dashboard_api_activity_actions_list(
        self,
        ordering: str | None = None,
        search: str | None = None,
    ) -> list[QuickAction]:
        """
        Get quick actions

        Retrieve quick action buttons for dashboard
        """
        url = "/cfg/dashboard/api/activity/actions/"
        _params = {
            k: v for k, v in {
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
        return [QuickAction.model_validate(item) for item in response.json()]


    async def dashboard_api_activity_recent_list(
        self,
        limit: int | None = None,
        ordering: str | None = None,
        search: str | None = None,
    ) -> list[ActivityEntry]:
        """
        Get recent activity

        Retrieve recent system activity entries
        """
        url = "/cfg/dashboard/api/activity/recent/"
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
        return [ActivityEntry.model_validate(item) for item in response.json()]


