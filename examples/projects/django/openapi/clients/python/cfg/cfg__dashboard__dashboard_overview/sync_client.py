from __future__ import annotations

import httpx

from .models import *


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
        response.raise_for_status()
        return DashboardOverview.model_validate(response.json())


