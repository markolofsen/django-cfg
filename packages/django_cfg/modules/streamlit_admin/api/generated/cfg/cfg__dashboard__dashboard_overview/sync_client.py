from __future__ import annotations

import httpx

from .models import (
    DashboardOverview,
)


class SyncCfgDashboardOverviewAPI:
    """Synchronous API endpoints for Dashboard - Overview."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def dashboard_api_overview_overview_retrieve(self) -> DashboardOverview:
        """
        Get dashboard overview

        Retrieve complete dashboard data including stats, health, actions, and
        metrics
        """
        url = "/cfg/dashboard/api/overview/overview/"
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
        return DashboardOverview.model_validate(response.json())


