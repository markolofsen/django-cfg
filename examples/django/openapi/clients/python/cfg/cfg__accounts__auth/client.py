from __future__ import annotations

import httpx

from .models import *


class CfgAuthAPI:
    """API endpoints for Auth."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def token_refresh_create(self, data: TokenRefreshRequest) -> TokenRefresh:
        """Refresh JWT token."""
        url = "/django_cfg_accounts/token/refresh/"
        response = await self._client.post(url, json=data.model_dump() if data else None)
        response.raise_for_status()
        return TokenRefresh.model_validate(response.json())


