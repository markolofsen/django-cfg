from __future__ import annotations

import httpx

from .models import (
    DRFHealthCheck,
    QuickHealth,
)


class CfgHealthAPI:
    """API endpoints for Health."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def drf_retrieve(self) -> DRFHealthCheck:
        """
        Return comprehensive health check data.
        """
        url = "/cfg/health/drf/"
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
        return DRFHealthCheck.model_validate(response.json())


    async def drf_quick_retrieve(self) -> QuickHealth:
        """
        Return minimal health status.
        """
        url = "/cfg/health/drf/quick/"
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
        return QuickHealth.model_validate(response.json())


