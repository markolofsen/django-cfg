from __future__ import annotations

import httpx

from .models import *


class SyncCfgTestingAPI:
    """Synchronous API endpoints for Testing."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def test_create(self, data: TestEmailRequest) -> BulkEmailResponse:
        """
        Test Email Sending

        Send a test email to verify mailer configuration.
        """
        url = "/django_cfg_newsletter/test/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return BulkEmailResponse.model_validate(response.json())


