from __future__ import annotations

import httpx

from .models import *


class SyncCfgLeadSubmissionAPI:
    """Synchronous API endpoints for Lead Submission."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def cfg_leads_leads_submit_create(self, data: LeadSubmissionRequest) -> LeadSubmissionResponse:
        """
        Submit Lead Form

        Submit a new lead from frontend contact form with automatic Telegram
        notifications.
        """
        url = "/cfg/leads/leads/submit/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return LeadSubmissionResponse.model_validate(response.json())


