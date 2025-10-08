from __future__ import annotations

import httpx

from .models import *


class CfgAccountsAPI:
    """API endpoints for Accounts."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def otp_request_create(self, data: OTPRequestRequest) -> OTPRequestResponse:
        """Request OTP code to email or phone."""
        url = "/django_cfg_accounts/otp/request/"
        response = await self._client.post(url, json=data.model_dump() if data else None)
        response.raise_for_status()
        return OTPRequestResponse.model_validate(response.json())


    async def otp_verify_create(self, data: OTPVerifyRequest) -> OTPVerifyResponse:
        """Verify OTP code and return JWT tokens."""
        url = "/django_cfg_accounts/otp/verify/"
        response = await self._client.post(url, json=data.model_dump() if data else None)
        response.raise_for_status()
        return OTPVerifyResponse.model_validate(response.json())


