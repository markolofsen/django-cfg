from __future__ import annotations

import httpx

from .models import *


class SyncCfgLogsAPI:
    """Synchronous API endpoints for Logs."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def newsletter_logs_list(self, page: int | None = None, page_size: int | None = None) -> list[PaginatedEmailLogList]:
        """
        List Email Logs

        Get a list of email sending logs.
        """
        url = "/cfg/newsletter/logs/"
        response = self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        return PaginatedEmailLogList.model_validate(response.json())


