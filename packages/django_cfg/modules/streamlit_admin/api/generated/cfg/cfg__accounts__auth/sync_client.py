from __future__ import annotations

import httpx

from .models import (
    TokenRefresh,
    TokenRefreshRequest,
)


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
        response = self._client.post(url, json=data.model_dump(mode="json", exclude_unset=True, exclude_none=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return TokenRefresh.model_validate(response.json())


