from __future__ import annotations

import httpx

from .models import *


class CfgDashboardActivityAPI:
    """API endpoints for Dashboard - Activity."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def dashboard_api_activity_actions_list(self) -> None:
        """
        Get quick actions

        Retrieve quick action buttons for dashboard
        """
        url = "/cfg/dashboard/api/activity/actions/"
        response = await self._client.get(url)
        response.raise_for_status()
        return None


    async def dashboard_api_activity_recent_list(self, limit: int | None = None) -> None:
        """
        Get recent activity

        Retrieve recent system activity entries
        """
        url = "/cfg/dashboard/api/activity/recent/"
        response = await self._client.get(url, params={"limit": limit if limit is not None else None})
        response.raise_for_status()
        return None


