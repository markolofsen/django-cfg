from __future__ import annotations

import httpx

from .models import (
    JobActionResponse,
    JobDetail,
    JobListRequest,
    PaginatedJobListList,
)


class CfgRqJobsAPI:
    """API endpoints for RQ Jobs."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def list(
        self,
        ordering: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        queue: str | None = None,
        search: str | None = None,
        status: str | None = None,
    ) -> list[PaginatedJobListList]:
        """
        List all jobs

        Returns all jobs across all registries (queued, started, finished,
        failed, deferred, scheduled).
        """
        url = "/cfg/rq/jobs/"
        _params = {
            k: v for k, v in {
                "ordering": ordering,
                "page": page,
                "page_size": page_size,
                "queue": queue,
                "search": search,
                "status": status,
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
        return PaginatedJobListList.model_validate(response.json())


    async def retrieve(self, id: str) -> JobDetail:
        """
        Get job details

        Returns detailed information about a specific job.
        """
        url = f"/cfg/rq/jobs/{id}/"
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
        return JobDetail.model_validate(response.json())


    async def destroy(self, id: str) -> JobActionResponse:
        """
        Delete job

        Deletes a job from the queue.
        """
        url = f"/cfg/rq/jobs/{id}/"
        response = await self._client.delete(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return JobActionResponse.model_validate(response.json())


    async def cancel_create(
        self,
        id: str,
        data: JobListRequest,
        force: bool | None = None,
    ) -> JobActionResponse:
        """
        Cancel job

        Cancels a job. For queued jobs, cancels immediately. For running jobs,
        sets cancellation flag for cooperative cancellation. Use force=true to
        send SIGTERM (dangerous).
        """
        url = f"/cfg/rq/jobs/{id}/cancel/"
        _params = {
            k: v for k, v in {
                "force": force,
            }.items() if v is not None
        }
        response = await self._client.post(url, params=_params, json=data.model_dump(mode="json", exclude_unset=True, exclude_none=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return JobActionResponse.model_validate(response.json())


    async def requeue_create(self, id: str, data: JobListRequest) -> JobActionResponse:
        """
        Requeue job

        Requeues a failed job.
        """
        url = f"/cfg/rq/jobs/{id}/requeue/"
        response = await self._client.post(url, json=data.model_dump(mode="json", exclude_unset=True, exclude_none=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return JobActionResponse.model_validate(response.json())


