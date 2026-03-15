from __future__ import annotations

import httpx

from .models import (
    OTPErrorResponse,
    OTPRequestRequest,
    OTPRequestResponse,
    OTPVerifyRequest,
    OTPVerifyResponse,
)


class CfgAccountsAPI:
    """API endpoints for Accounts."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def otp_request_create(self, data: OTPRequestRequest) -> OTPRequestResponse:
        """
        Request OTP code to email or phone.
        """
        url = "/cfg/accounts/otp/request/"
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
        return OTPRequestResponse.model_validate(response.json())


    async def otp_verify_create(self, data: OTPVerifyRequest) -> OTPVerifyResponse:
        """
        Verify OTP code and return JWT tokens or 2FA session. If user has 2FA
        enabled: - Returns requires_2fa=True with session_id - Client must
        complete 2FA verification at /cfg/totp/verify/ If user has no 2FA: -
        Returns JWT tokens and user data directly
        """
        url = "/cfg/accounts/otp/verify/"
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
        return OTPVerifyResponse.model_validate(response.json())


