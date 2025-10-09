from __future__ import annotations

import httpx

from .models import *


class SyncCfgCampaignsAPI:
    """Synchronous API endpoints for Campaigns."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def cfg_newsletter_campaigns_list(self, page: int | None = None, page_size: int | None = None) -> list[PaginatedNewsletterCampaignList]:
        """
        List Newsletter Campaigns

        Get a list of all newsletter campaigns.
        """
        url = "/cfg/newsletter/campaigns/"
        response = self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedNewsletterCampaignList.model_validate(item) for item in data.get("results", [])]


    def cfg_newsletter_campaigns_create(self, data: NewsletterCampaignRequest) -> NewsletterCampaign:
        """
        Create Newsletter Campaign

        Create a new newsletter campaign.
        """
        url = "/cfg/newsletter/campaigns/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return NewsletterCampaign.model_validate(response.json())


    def cfg_newsletter_campaigns_retrieve(self, id: int) -> NewsletterCampaign:
        """
        Get Campaign Details

        Retrieve details of a specific newsletter campaign.
        """
        url = f"/cfg/newsletter/campaigns/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return NewsletterCampaign.model_validate(response.json())


    def cfg_newsletter_campaigns_update(self, id: int, data: NewsletterCampaignRequest) -> NewsletterCampaign:
        """
        Update Campaign

        Update a newsletter campaign.
        """
        url = f"/cfg/newsletter/campaigns/{id}/"
        response = self._client.put(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return NewsletterCampaign.model_validate(response.json())


    def cfg_newsletter_campaigns_destroy(self, id: int) -> None:
        """
        Delete Campaign

        Delete a newsletter campaign.
        """
        url = f"/cfg/newsletter/campaigns/{id}/"
        response = self._client.delete(url)
        response.raise_for_status()


    def cfg_newsletter_campaigns_send_create(self, data: SendCampaignRequest) -> SendCampaignResponse:
        """
        Send Newsletter Campaign

        Send a newsletter campaign to all subscribers.
        """
        url = "/cfg/newsletter/campaigns/send/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return SendCampaignResponse.model_validate(response.json())


