from __future__ import annotations

import httpx

from .models import *


class CfgCampaignsAPI:
    """API endpoints for Campaigns."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def list(self, page: int | None = None, page_size: int | None = None) -> list[PaginatedNewsletterCampaignList]:
        """
        List Newsletter Campaigns

        Get a list of all newsletter campaigns.
        """
        url = "/django_cfg_newsletter/campaigns/"
        response = await self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedNewsletterCampaignList.model_validate(item) for item in data.get("results", [])]


    async def create(self, data: NewsletterCampaignRequest) -> NewsletterCampaign:
        """
        Create Newsletter Campaign

        Create a new newsletter campaign.
        """
        url = "/django_cfg_newsletter/campaigns/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return NewsletterCampaign.model_validate(response.json())


    async def retrieve(self, id: int) -> NewsletterCampaign:
        """
        Get Campaign Details

        Retrieve details of a specific newsletter campaign.
        """
        url = f"/django_cfg_newsletter/campaigns/{id}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return NewsletterCampaign.model_validate(response.json())


    async def update(self, id: int, data: NewsletterCampaignRequest) -> NewsletterCampaign:
        """
        Update Campaign

        Update a newsletter campaign.
        """
        url = f"/django_cfg_newsletter/campaigns/{id}/"
        response = await self._client.put(url, json=data.model_dump())
        response.raise_for_status()
        return NewsletterCampaign.model_validate(response.json())


    async def destroy(self, id: int) -> None:
        """
        Delete Campaign

        Delete a newsletter campaign.
        """
        url = f"/django_cfg_newsletter/campaigns/{id}/"
        response = await self._client.delete(url)
        response.raise_for_status()
        return None


    async def send_create(self, data: SendCampaignRequest) -> SendCampaignResponse:
        """
        Send Newsletter Campaign

        Send a newsletter campaign to all subscribers.
        """
        url = "/django_cfg_newsletter/campaigns/send/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return SendCampaignResponse.model_validate(response.json())


