from __future__ import annotations

import httpx

from .models import *


class SyncCfgBulkEmailAPI:
    """Synchronous API endpoints for Bulk Email."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def bulk_create(self, data: BulkEmailRequest) -> BulkEmailResponse:
        """
        Send Bulk Email

        Send bulk emails to multiple recipients using base email template.
        """
        url = "/django_cfg_newsletter/bulk/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return BulkEmailResponse.model_validate(response.json())


