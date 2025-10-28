from __future__ import annotations

import httpx

from .models import *


class CfgDashboardSystemAPI:
    """API endpoints for Dashboard - System."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def dashboard_api_system_health_retrieve(self) -> SystemHealth:
        """
        Get system health status

        Retrieve overall system health including all component checks
        """
        url = "/cfg/dashboard/api/system/health/"
        response = await self._client.get(url)
        response.raise_for_status()
        return SystemHealth.model_validate(response.json())


    async def dashboard_api_system_metrics_retrieve(self) -> SystemMetrics:
        """
        Get system metrics

        Retrieve system performance metrics (CPU, memory, disk, etc.)
        """
        url = "/cfg/dashboard/api/system/metrics/"
        response = await self._client.get(url)
        response.raise_for_status()
        return SystemMetrics.model_validate(response.json())


