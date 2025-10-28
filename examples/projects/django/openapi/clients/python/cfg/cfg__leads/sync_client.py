from __future__ import annotations

import httpx

from .models import *


class SyncCfgLeadsAPI:
    """Synchronous API endpoints for Leads."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def list(self, page: int | None = None, page_size: int | None = None) -> list[PaginatedLeadSubmissionList]:
        """
        ViewSet for Lead model. Provides only submission functionality for leads
        from frontend forms.
        """
        url = "/cfg/leads/"
        response = self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        return PaginatedLeadSubmissionList.model_validate(response.json())


    def create(self, data: LeadSubmissionRequest) -> LeadSubmission:
        """
        ViewSet for Lead model. Provides only submission functionality for leads
        from frontend forms.
        """
        url = "/cfg/leads/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return LeadSubmission.model_validate(response.json())


    def retrieve(self, id: int) -> LeadSubmission:
        """
        ViewSet for Lead model. Provides only submission functionality for leads
        from frontend forms.
        """
        url = f"/cfg/leads/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return LeadSubmission.model_validate(response.json())


    def update(self, id: int, data: LeadSubmissionRequest) -> LeadSubmission:
        """
        ViewSet for Lead model. Provides only submission functionality for leads
        from frontend forms.
        """
        url = f"/cfg/leads/{id}/"
        response = self._client.put(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return LeadSubmission.model_validate(response.json())


    def partial_update(self, id: int, data: PatchedLeadSubmissionRequest | None = None) -> LeadSubmission:
        """
        ViewSet for Lead model. Provides only submission functionality for leads
        from frontend forms.
        """
        url = f"/cfg/leads/{id}/"
        response = self._client.patch(url, json=data.model_dump(exclude_unset=True) if data is not None else None)
        response.raise_for_status()
        return LeadSubmission.model_validate(response.json())


    def destroy(self, id: int) -> None:
        """
        ViewSet for Lead model. Provides only submission functionality for leads
        from frontend forms.
        """
        url = f"/cfg/leads/{id}/"
        response = self._client.delete(url)
        response.raise_for_status()


