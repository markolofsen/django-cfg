from __future__ import annotations

import httpx

from .models import (
    ConfirmSetupRequest,
    ConfirmSetupResponse,
    SetupRequest,
    SetupResponse,
)


class CfgTotpSetupAPI:
    """API endpoints for TOTP Setup."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def create(self, data: SetupRequest) -> SetupResponse:
        """
        Start 2FA setup process. Creates a new TOTP device and returns QR code
        for scanning.
        """
        url = "/cfg/totp/setup/"
        response = await self._client.post(url, json=data.model_dump(mode="json", exclude_unset=True, exclude_none=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return SetupResponse.model_validate(response.json())


    async def confirm_create(self, data: ConfirmSetupRequest) -> ConfirmSetupResponse:
        """
        Confirm 2FA setup with first valid code. Activates the device and
        generates backup codes.
        """
        url = "/cfg/totp/setup/confirm/"
        response = await self._client.post(url, json=data.model_dump(mode="json", exclude_unset=True, exclude_none=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return ConfirmSetupResponse.model_validate(response.json())


