from __future__ import annotations

import httpx

from .models import *


class SyncCfgAuthAPI:
    """Synchronous API endpoints for Auth."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def accounts_token_refresh_create(self, data: TokenRefreshRequest) -> TokenRefresh:
        """
        Refresh JWT token.
        """
        url = "/cfg/accounts/token/refresh/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return TokenRefresh.model_validate(response.json())


