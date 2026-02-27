from __future__ import annotations

import httpx

from .models import (
    PaginatedScheduledJobList,
    ScheduleActionResponse,
    ScheduleCreateRequest,
    ScheduledJob,
)


class SyncCfgRqSchedulesAPI:
    """Synchronous API endpoints for RQ Schedules."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def list(
        self,
        ordering: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        queue: str | None = None,
        search: str | None = None,
    ) -> list[PaginatedScheduledJobList]:
        """
        List scheduled jobs

        Returns list of all scheduled jobs across all queues.
        """
        url = "/cfg/rq/schedules/"
        _params = {
            k: v for k, v in {
                "ordering": ordering,
                "page": page,
                "page_size": page_size,
                "queue": queue,
                "search": search,
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
        return PaginatedScheduledJobList.model_validate(response.json())


    def create(self, data: ScheduleCreateRequest) -> ScheduleActionResponse:
        """
        Create scheduled job

        Schedule a job to run at specific time, interval, or cron schedule.
        """
        url = "/cfg/rq/schedules/"
        response = self._client.post(url, json=data.model_dump(mode="json", exclude_unset=True, exclude_none=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return ScheduleActionResponse.model_validate(response.json())


    def retrieve(self, id: str, pk: str, queue: str | None = None) -> ScheduledJob:
        """
        Get scheduled job details

        Returns detailed information about a specific scheduled job.
        """
        url = f"/cfg/rq/schedules/{id}/"
        _params = {
            k: v for k, v in {
                "queue": queue,
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
        return ScheduledJob.model_validate(response.json())


    def destroy(self, id: str, pk: str, queue: str | None = None) -> ScheduleActionResponse:
        """
        Cancel scheduled job

        Cancel a scheduled job by ID.
        """
        url = f"/cfg/rq/schedules/{id}/"
        _params = {
            k: v for k, v in {
                "queue": queue,
            }.items() if v is not None
        }
        response = self._client.delete(url, params=_params)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return ScheduleActionResponse.model_validate(response.json())


