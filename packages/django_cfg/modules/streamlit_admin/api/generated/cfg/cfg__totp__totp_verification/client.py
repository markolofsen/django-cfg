from __future__ import annotations

import httpx

from .models import (
    VerifyBackupRequest,
    VerifyRequest,
    VerifyResponse,
)


class CfgTotpVerificationAPI:
    """API endpoints for TOTP Verification."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def totp_verify_create(self, data: VerifyRequest) -> VerifyResponse:
        """
        Verify TOTP code for 2FA session. Completes authentication and returns
        JWT tokens on success.
        """
        url = "/cfg/totp/verify/"
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
        return VerifyResponse.model_validate(response.json())


    async def totp_verify_backup_create(self, data: VerifyBackupRequest) -> VerifyResponse:
        """
        Verify backup recovery code for 2FA session. Alternative verification
        method when TOTP device unavailable.
        """
        url = "/cfg/totp/verify/backup/"
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
        return VerifyResponse.model_validate(response.json())


