from __future__ import annotations

import httpx

from .models import (
    Worker,
    WorkerStats,
)


class CfgRqWorkersAPI:
    """API endpoints for RQ Workers."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def list(self, queue: str | None = None, state: str | None = None) -> list[Worker]:
        """
        List all workers

        Returns list of all RQ workers with their current state. Supports
        filtering by state and queue.
        """
        url = "/cfg/rq/workers/"
        _params = {
            k: v for k, v in {
                "queue": queue,
                "state": state,
            }.items() if v is not None
        }
        response = await self._client.get(url, params=_params)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return [Worker.model_validate(item) for item in response.json()]


    async def stats_retrieve(self) -> WorkerStats:
        """
        Get worker statistics

        Returns aggregated statistics for all workers.
        """
        url = "/cfg/rq/workers/stats/"
        response = await self._client.get(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return WorkerStats.model_validate(response.json())


