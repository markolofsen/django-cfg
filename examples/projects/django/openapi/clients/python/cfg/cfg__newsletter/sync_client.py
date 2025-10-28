from __future__ import annotations

import httpx

from .models import *


class SyncCfgNewsletterAPI:
    """Synchronous API endpoints for Newsletter."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def campaigns_partial_update(self, id: int, data: PatchedNewsletterCampaignRequest | None = None) -> NewsletterCampaign:
        """
        Retrieve, update, or delete a newsletter campaign.
        """
        url = f"/cfg/newsletter/campaigns/{id}/"
        response = self._client.patch(url, json=data.model_dump(exclude_unset=True) if data is not None else None)
        response.raise_for_status()
        return NewsletterCampaign.model_validate(response.json())


    def unsubscribe_update(self, data: UnsubscribeRequest) -> Unsubscribe:
        """
        Handle newsletter unsubscriptions.
        """
        url = "/cfg/newsletter/unsubscribe/"
        response = self._client.put(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return Unsubscribe.model_validate(response.json())


    def unsubscribe_partial_update(self, data: PatchedUnsubscribeRequest | None = None) -> Unsubscribe:
        """
        Handle newsletter unsubscriptions.
        """
        url = "/cfg/newsletter/unsubscribe/"
        response = self._client.patch(url, json=data.model_dump(exclude_unset=True) if data is not None else None)
        response.raise_for_status()
        return Unsubscribe.model_validate(response.json())


