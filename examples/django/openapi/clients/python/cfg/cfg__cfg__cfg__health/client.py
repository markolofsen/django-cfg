from __future__ import annotations

import httpx

from .models import *


class CfgHealthAPI:
    """API endpoints for Cfg Health."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def cfg_health_drf_retrieve(self) -> HealthCheck:
        """
        Return comprehensive health check data.
        """
        url = "/cfg/health/drf/"
        response = await self._client.get(url)
        response.raise_for_status()
        return HealthCheck.model_validate(response.json())


    async def cfg_health_drf_quick_retrieve(self) -> QuickHealth:
        """
        Return minimal health status.
        """
        url = "/cfg/health/drf/quick/"
        response = await self._client.get(url)
        response.raise_for_status()
        return QuickHealth.model_validate(response.json())


