from __future__ import annotations

import httpx

from .models import *


class CfgLeadsAPI:
    """API endpoints for Leads."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def list(self, page: int | None = None, page_size: int | None = None) -> list[PaginatedLeadSubmissionList]:
        """
        ViewSet for Lead model. Provides only submission functionality for leads
        from frontend forms.
        """
        url = "/django_cfg_leads/leads/"
        response = await self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedLeadSubmissionList.model_validate(item) for item in data.get("results", [])]


    async def create(self, data: LeadSubmissionRequest) -> LeadSubmission:
        """
        ViewSet for Lead model. Provides only submission functionality for leads
        from frontend forms.
        """
        url = "/django_cfg_leads/leads/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return LeadSubmission.model_validate(response.json())


    async def retrieve(self, id: int) -> LeadSubmission:
        """
        ViewSet for Lead model. Provides only submission functionality for leads
        from frontend forms.
        """
        url = f"/django_cfg_leads/leads/{id}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return LeadSubmission.model_validate(response.json())


    async def update(self, id: int, data: LeadSubmissionRequest) -> LeadSubmission:
        """
        ViewSet for Lead model. Provides only submission functionality for leads
        from frontend forms.
        """
        url = f"/django_cfg_leads/leads/{id}/"
        response = await self._client.put(url, json=data.model_dump())
        response.raise_for_status()
        return LeadSubmission.model_validate(response.json())


    async def partial_update(self, id: int, data: PatchedLeadSubmissionRequest | None = None) -> LeadSubmission:
        """
        ViewSet for Lead model. Provides only submission functionality for leads
        from frontend forms.
        """
        url = f"/django_cfg_leads/leads/{id}/"
        response = await self._client.patch(url, json=data.model_dump() if data is not None else None)
        response.raise_for_status()
        return LeadSubmission.model_validate(response.json())


    async def destroy(self, id: int) -> None:
        """
        ViewSet for Lead model. Provides only submission functionality for leads
        from frontend forms.
        """
        url = f"/django_cfg_leads/leads/{id}/"
        response = await self._client.delete(url)
        response.raise_for_status()
        return None


