from __future__ import annotations

import httpx

from .models import (
    ConnectionTokenResponse,
)


class SyncCfgCentrifugoAuthAPI:
    """Synchronous API endpoints for Centrifugo Auth."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def token_retrieve(self) -> ConnectionTokenResponse:
        """
        Get Centrifugo connection token

        Generate JWT token for WebSocket connection to Centrifugo. Token
        includes user's allowed channels based on their permissions. Requires
        authentication.
        """
        url = "/cfg/centrifugo/auth/token/"
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
        return ConnectionTokenResponse.model_validate(response.json())


