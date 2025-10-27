from __future__ import annotations

import httpx

from .models import *


class CfgEndpointsAPI:
    """API endpoints for Endpoints."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def drf_retrieve(self) -> EndpointsStatus:
        """
        Return endpoints status data.
        """
        url = "/cfg/endpoints/drf/"
        response = await self._client.get(url)
        response.raise_for_status()
        return EndpointsStatus.model_validate(response.json())


    async def urls_retrieve(self) -> list[URLsList]:
        """
        Return all registered URLs.
        """
        url = "/cfg/endpoints/urls/"
        response = await self._client.get(url)
        response.raise_for_status()
        return URLsList.model_validate(response.json())


    async def urls_compact_retrieve(self) -> None:
        """
        Return compact URL list.
        """
        url = "/cfg/endpoints/urls/compact/"
        response = await self._client.get(url)
        response.raise_for_status()
        return None


