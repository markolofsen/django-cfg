from __future__ import annotations

import httpx

from .models import *


class CfgAccountsAPI:
    """API endpoints for Cfg Accounts."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def cfg_accounts_otp_request_create(self, data: OTPRequestRequest) -> OTPRequestResponse:
        """
        Request OTP code to email or phone.
        """
        url = "/cfg/accounts/otp/request/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return OTPRequestResponse.model_validate(response.json())


    async def cfg_accounts_otp_verify_create(self, data: OTPVerifyRequest) -> OTPVerifyResponse:
        """
        Verify OTP code and return JWT tokens.
        """
        url = "/cfg/accounts/otp/verify/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return OTPVerifyResponse.model_validate(response.json())


