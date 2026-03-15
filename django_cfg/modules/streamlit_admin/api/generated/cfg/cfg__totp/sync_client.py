from __future__ import annotations

import httpx


class SyncCfgTotpAPI:
    """Synchronous API endpoints for Totp."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def devices_destroy(self, id: str) -> None:
        """
        Delete a TOTP device. Requires verification code if removing the
        last/primary device.
        """
        url = f"/cfg/totp/devices/{id}/"
        response = self._client.delete(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )


