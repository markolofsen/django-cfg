from __future__ import annotations

import httpx

from .models import (
    JobActionResponse,
    JobListRequest,
    PaginatedJobListList,
)


class SyncCfgRqRegistriesAPI:
    """Synchronous API endpoints for RQ Registries."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def rq_jobs_registries_deferred_list(
        self,
        ordering: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        queue: str | None = None,
        search: str | None = None,
    ) -> list[PaginatedJobListList]:
        """
        List deferred jobs

        Returns list of all deferred jobs from deferred job registry.
        """
        url = "/cfg/rq/jobs/registries/deferred/"
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
        return PaginatedJobListList.model_validate(response.json())


    def rq_jobs_registries_failed_list(
        self,
        ordering: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        queue: str | None = None,
        search: str | None = None,
    ) -> list[PaginatedJobListList]:
        """
        List failed jobs

        Returns list of all failed jobs from failed job registry.
        """
        url = "/cfg/rq/jobs/registries/failed/"
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
        return PaginatedJobListList.model_validate(response.json())


    def rq_jobs_registries_failed_clear_create(
        self,
        data: JobListRequest,
        queue: str,
    ) -> JobActionResponse:
        """
        Clear failed jobs registry

        Removes all jobs from the failed job registry.
        """
        url = "/cfg/rq/jobs/registries/failed/clear/"
        _params = {
            k: v for k, v in {
                "queue": queue,
            }.items() if v is not None
        }
        response = self._client.post(url, params=_params, json=data.model_dump(mode="json", exclude_unset=True, exclude_none=True))
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


    def rq_jobs_registries_failed_requeue_all_create(
        self,
        data: JobListRequest,
        queue: str,
    ) -> JobActionResponse:
        """
        Requeue all failed jobs

        Requeues all failed jobs in the failed job registry.
        """
        url = "/cfg/rq/jobs/registries/failed/requeue-all/"
        _params = {
            k: v for k, v in {
                "queue": queue,
            }.items() if v is not None
        }
        response = self._client.post(url, params=_params, json=data.model_dump(mode="json", exclude_unset=True, exclude_none=True))
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


    def rq_jobs_registries_finished_list(
        self,
        ordering: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        queue: str | None = None,
        search: str | None = None,
    ) -> list[PaginatedJobListList]:
        """
        List finished jobs

        Returns list of all finished jobs from finished job registry.
        """
        url = "/cfg/rq/jobs/registries/finished/"
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
        return PaginatedJobListList.model_validate(response.json())


    def rq_jobs_registries_finished_clear_create(
        self,
        data: JobListRequest,
        queue: str,
    ) -> JobActionResponse:
        """
        Clear finished jobs registry

        Removes all jobs from the finished job registry.
        """
        url = "/cfg/rq/jobs/registries/finished/clear/"
        _params = {
            k: v for k, v in {
                "queue": queue,
            }.items() if v is not None
        }
        response = self._client.post(url, params=_params, json=data.model_dump(mode="json", exclude_unset=True, exclude_none=True))
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


    def rq_jobs_registries_started_list(
        self,
        ordering: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        queue: str | None = None,
        search: str | None = None,
    ) -> list[PaginatedJobListList]:
        """
        List started jobs

        Returns list of all currently running jobs from started job registry.
        """
        url = "/cfg/rq/jobs/registries/started/"
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
        return PaginatedJobListList.model_validate(response.json())


