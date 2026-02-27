from __future__ import annotations

import httpx

from .models import (
    QueueDetail,
    QueueStats,
)


class SyncCfgRqQueuesAPI:
    """Synchronous API endpoints for RQ Queues."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def list(self, name: str | None = None) -> list[QueueStats]:
        """
        List all queues

        Returns list of all configured RQ queues with statistics. Supports
        filtering by queue name.
        """
        url = "/cfg/rq/queues/"
        _params = {
            k: v for k, v in {
                "name": name,
            }.items() if v is not None
        }
        response = self._client.get(url, params=_params)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return [QueueStats.model_validate(item) for item in response.json()]


    def retrieve(self, id: str) -> QueueDetail:
        """
        Get queue details

        Returns detailed information about a specific queue.
        """
        url = f"/cfg/rq/queues/{id}/"
        response = self._client.get(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return QueueDetail.model_validate(response.json())


    def empty_create(self, id: str) -> None:
        """
        Empty queue

        Removes all jobs from the specified queue.
        """
        url = f"/cfg/rq/queues/{id}/empty/"
        response = self._client.post(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )


    def jobs_retrieve(
        self,
        id: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> None:
        """
        Get queue jobs

        Returns list of job IDs in the queue.
        """
        url = f"/cfg/rq/queues/{id}/jobs/"
        _params = {
            k: v for k, v in {
                "limit": limit,
                "offset": offset,
            }.items() if v is not None
        }
        response = self._client.get(url, params=_params)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )


