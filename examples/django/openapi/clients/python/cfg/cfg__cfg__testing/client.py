from __future__ import annotations

import httpx

from .models import *


class CfgTestingAPI:
    """API endpoints for Testing."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def cfg_newsletter_test_create(self, data: TestEmailRequest) -> BulkEmailResponse:
        """
        Test Email Sending

        Send a test email to verify mailer configuration.
        """
        url = "/cfg/newsletter/test/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return BulkEmailResponse.model_validate(response.json())


