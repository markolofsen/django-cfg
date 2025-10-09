from __future__ import annotations

import httpx

from .models import *


class SyncCfgEndpointsAPI:
    """Synchronous API endpoints for Cfg Endpoints."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def cfg_endpoints_drf_retrieve(self) -> EndpointsStatus:
        """
        Return endpoints status data.
        """
        url = "/cfg/endpoints/drf/"
        response = self._client.get(url)
        response.raise_for_status()
        return EndpointsStatus.model_validate(response.json())


