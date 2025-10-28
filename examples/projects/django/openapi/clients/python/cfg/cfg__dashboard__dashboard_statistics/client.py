from __future__ import annotations

import httpx

from .models import *


class CfgDashboardStatisticsAPI:
    """API endpoints for Dashboard - Statistics."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def dashboard_api_statistics_apps_list(self) -> None:
        """
        Get application statistics

        Retrieve statistics for all enabled django-cfg applications
        """
        url = "/cfg/dashboard/api/statistics/apps/"
        response = await self._client.get(url)
        response.raise_for_status()
        return None


    async def dashboard_api_statistics_cards_list(self) -> None:
        """
        Get statistics cards

        Retrieve dashboard statistics cards with key metrics
        """
        url = "/cfg/dashboard/api/statistics/cards/"
        response = await self._client.get(url)
        response.raise_for_status()
        return None


    async def dashboard_api_statistics_users_retrieve(self) -> UserStatistics:
        """
        Get user statistics

        Retrieve user-related statistics
        """
        url = "/cfg/dashboard/api/statistics/users/"
        response = await self._client.get(url)
        response.raise_for_status()
        return UserStatistics.model_validate(response.json())


