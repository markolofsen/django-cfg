from __future__ import annotations

import httpx

from .models import *


class CfgDashboardApiZonesAPI:
    """API endpoints for Dashboard - API Zones."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def list(self) -> None:
        """
        Get all API zones

        Retrieve all OpenAPI zones/groups with their configuration
        """
        url = "/cfg/dashboard/api/zones/"
        response = await self._client.get(url)
        response.raise_for_status()
        return None


    async def summary_retrieve(self) -> APIZonesSummary:
        """
        Get zones summary

        Retrieve zones summary with statistics
        """
        url = "/cfg/dashboard/api/zones/summary/"
        response = await self._client.get(url)
        response.raise_for_status()
        return APIZonesSummary.model_validate(response.json())


