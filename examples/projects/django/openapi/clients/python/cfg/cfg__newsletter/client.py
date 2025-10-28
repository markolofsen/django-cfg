from __future__ import annotations

import httpx

from .models import *


class CfgNewsletterAPI:
    """API endpoints for Newsletter."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def campaigns_partial_update(self, id: int, data: PatchedNewsletterCampaignRequest | None = None) -> NewsletterCampaign:
        """
        Retrieve, update, or delete a newsletter campaign.
        """
        url = f"/cfg/newsletter/campaigns/{id}/"
        response = await self._client.patch(url, json=data.model_dump() if data is not None else None)
        response.raise_for_status()
        return NewsletterCampaign.model_validate(response.json())


    async def unsubscribe_update(self, data: UnsubscribeRequest) -> Unsubscribe:
        """
        Handle newsletter unsubscriptions.
        """
        url = "/cfg/newsletter/unsubscribe/"
        response = await self._client.put(url, json=data.model_dump())
        response.raise_for_status()
        return Unsubscribe.model_validate(response.json())


    async def unsubscribe_partial_update(self, data: PatchedUnsubscribeRequest | None = None) -> Unsubscribe:
        """
        Handle newsletter unsubscriptions.
        """
        url = "/cfg/newsletter/unsubscribe/"
        response = await self._client.patch(url, json=data.model_dump() if data is not None else None)
        response.raise_for_status()
        return Unsubscribe.model_validate(response.json())


