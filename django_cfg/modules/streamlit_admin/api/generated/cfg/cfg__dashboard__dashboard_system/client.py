from __future__ import annotations

import httpx

from .models import (
    SystemHealth,
    SystemMetrics,
)


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
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return SystemHealth.model_validate(response.json())


    async def dashboard_api_system_metrics_retrieve(self) -> SystemMetrics:
        """
        Get system metrics

        Retrieve system performance metrics (CPU, memory, disk, etc.)
        """
        url = "/cfg/dashboard/api/system/metrics/"
        response = await self._client.get(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return SystemMetrics.model_validate(response.json())


