from __future__ import annotations

import httpx

from .models import *


class SyncCfgNewslettersAPI:
    """Synchronous API endpoints for Newsletters."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def newsletter_newsletters_list(self, page: int | None = None, page_size: int | None = None) -> list[PaginatedNewsletterList]:
        """
        List Active Newsletters

        Get a list of all active newsletters available for subscription.
        """
        url = "/cfg/newsletter/newsletters/"
        response = self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedNewsletterList.model_validate(item) for item in data.get("results", [])]


    def newsletter_newsletters_retrieve(self, id: int) -> Newsletter:
        """
        Get Newsletter Details

        Retrieve details of a specific newsletter.
        """
        url = f"/cfg/newsletter/newsletters/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return Newsletter.model_validate(response.json())


