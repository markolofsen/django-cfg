from __future__ import annotations

import httpx

from .models import (
    GRPCHealthCheck,
    GRPCOverviewStats,
    MethodList,
    PaginatedRecentRequestList,
)


class SyncCfgGrpcMonitoringAPI:
    """Synchronous API endpoints for Grpc Monitoring."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def grpc_monitor_health_retrieve(self) -> GRPCHealthCheck:
        """
        Get gRPC health status

        Returns the current health status of the gRPC server.
        """
        url = "/cfg/grpc/monitor/health/"
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
        return GRPCHealthCheck.model_validate(response.json())


    def grpc_monitor_methods_retrieve(
        self,
        hours: int | None = None,
        service: str | None = None,
    ) -> list[MethodList]:
        """
        Get method statistics

        Returns statistics grouped by method.
        """
        url = "/cfg/grpc/monitor/methods/"
        _params = {
            k: v for k, v in {
                "hours": hours,
                "service": service,
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
        return MethodList.model_validate(response.json())


    def grpc_monitor_overview_retrieve(self, hours: int | None = None) -> GRPCOverviewStats:
        """
        Get overview statistics

        Returns overview statistics for gRPC requests.
        """
        url = "/cfg/grpc/monitor/overview/"
        _params = {
            k: v for k, v in {
                "hours": hours,
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
        return GRPCOverviewStats.model_validate(response.json())


    def grpc_monitor_requests_list(
        self,
        method: str | None = None,
        ordering: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        search: str | None = None,
        service: str | None = None,
        status: str | None = None,
    ) -> list[PaginatedRecentRequestList]:
        """
        Get recent requests

        Returns a list of recent gRPC requests with their details. Uses standard
        DRF pagination.
        """
        url = "/cfg/grpc/monitor/requests/"
        _params = {
            k: v for k, v in {
                "method": method,
                "ordering": ordering,
                "page": page,
                "page_size": page_size,
                "search": search,
                "service": service,
                "status": status,
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
        return PaginatedRecentRequestList.model_validate(response.json())


    def grpc_monitor_timeline_retrieve(
        self,
        hours: int | None = None,
        interval: str | None = None,
    ) -> None:
        """
        Get request timeline

        Returns hourly or daily breakdown of request counts for charts.
        """
        url = "/cfg/grpc/monitor/timeline/"
        _params = {
            k: v for k, v in {
                "hours": hours,
                "interval": interval,
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


