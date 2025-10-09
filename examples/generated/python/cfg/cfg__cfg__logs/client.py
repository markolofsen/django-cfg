from __future__ import annotations

import httpx

from .models import *


class CfgLogsAPI:
    """API endpoints for Logs."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def cfg_newsletter_logs_list(self, page: int | None = None, page_size: int | None = None) -> list[PaginatedEmailLogList]:
        """
        List Email Logs

        Get a list of email sending logs.
        """
        url = "/cfg/newsletter/logs/"
        response = await self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedEmailLogList.model_validate(item) for item in data.get("results", [])]


