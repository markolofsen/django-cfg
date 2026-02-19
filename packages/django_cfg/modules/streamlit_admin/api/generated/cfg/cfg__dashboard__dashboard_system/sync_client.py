from __future__ import annotations

import httpx

from .models import (
    SystemHealth,
    SystemMetrics,
)


class SyncCfgDashboardSystemAPI:
    """Synchronous API endpoints for Dashboard - System."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def dashboard_api_system_health_retrieve(self) -> SystemHealth:
        """
        Get system health status

        Retrieve overall system health including all component checks
        """
        url = "/cfg/dashboard/api/system/health/"
        response = self._client.get(url)
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


    def dashboard_api_system_metrics_retrieve(self) -> SystemMetrics:
        """
        Get system metrics

        Retrieve system performance metrics (CPU, memory, disk, etc.)
        """
        url = "/cfg/dashboard/api/system/metrics/"
        response = self._client.get(url)
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


