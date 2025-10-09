from __future__ import annotations

import httpx

from .models import *


class CfgBulkEmailAPI:
    """API endpoints for Bulk Email."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def cfg_newsletter_bulk_create(self, data: BulkEmailRequest) -> BulkEmailResponse:
        """
        Send Bulk Email

        Send bulk emails to multiple recipients using base email template.
        """
        url = "/cfg/newsletter/bulk/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return BulkEmailResponse.model_validate(response.json())


