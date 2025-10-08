from __future__ import annotations

import httpx

from .models import *


class CfgLeadSubmissionAPI:
    """API endpoints for Lead Submission."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def leads_submit_create(self, data: LeadSubmissionRequest) -> LeadSubmissionResponse:
        """Submit Lead Form

    Submit a new lead from frontend contact form with automatic Telegram
    notifications."""
        url = "/django_cfg_leads/leads/submit/"
        response = await self._client.post(url, json=data.model_dump() if data else None)
        response.raise_for_status()
        return LeadSubmissionResponse.model_validate(response.json())


