from __future__ import annotations

import httpx

from .models import (
    CentrifugoHealthCheck,
    CentrifugoOverviewStats,
    ChannelList,
    PaginatedPublishList,
    TimelineResponse,
)


class SyncCfgCentrifugoMonitoringAPI:
    """Synchronous API endpoints for Centrifugo Monitoring."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def centrifugo_monitor_channels_retrieve(
        self,
        hours: int | None = None,
    ) -> list[ChannelList]:
        """
        Get channel statistics

        Returns statistics grouped by channel.
        """
        url = "/cfg/centrifugo/monitor/channels/"
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
        return ChannelList.model_validate(response.json())


    def centrifugo_monitor_health_retrieve(self) -> CentrifugoHealthCheck:
        """
        Get Centrifugo health status

        Returns the current health status of the Centrifugo client.
        """
        url = "/cfg/centrifugo/monitor/health/"
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
        return CentrifugoHealthCheck.model_validate(response.json())


    def centrifugo_monitor_overview_retrieve(
        self,
        hours: int | None = None,
    ) -> CentrifugoOverviewStats:
        """
        Get overview statistics

        Returns overview statistics for Centrifugo publishes.
        """
        url = "/cfg/centrifugo/monitor/overview/"
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
        return CentrifugoOverviewStats.model_validate(response.json())


    def centrifugo_monitor_publishes_list(
        self,
        channel: str | None = None,
        ordering: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        search: str | None = None,
        status: str | None = None,
    ) -> list[PaginatedPublishList]:
        """
        Get recent publishes

        Returns a paginated list of recent Centrifugo publishes with their
        details. Uses standard DRF pagination.
        """
        url = "/cfg/centrifugo/monitor/publishes/"
        _params = {
            k: v for k, v in {
                "channel": channel,
                "ordering": ordering,
                "page": page,
                "page_size": page_size,
                "search": search,
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
        return PaginatedPublishList.model_validate(response.json())


    def centrifugo_monitor_timeline_retrieve(
        self,
        hours: int | None = None,
        interval: str | None = None,
    ) -> TimelineResponse:
        """
        Get publish timeline

        Returns hourly or daily breakdown of publish counts for charts.
        """
        url = "/cfg/centrifugo/monitor/timeline/"
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
        return TimelineResponse.model_validate(response.json())


