from __future__ import annotations

import httpx

from .models import *


class SyncCfgCentrifugoMonitoringAPI:
    """Synchronous API endpoints for Centrifugo Monitoring."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def centrifugo_monitor_health_retrieve(self) -> HealthCheck:
        """
        Get Centrifugo health status

        Returns the current health status of the Centrifugo client.
        """
        url = "/cfg/centrifugo/monitor/health/"
        response = self._client.get(url)
        response.raise_for_status()
        return HealthCheck.model_validate(response.json())


    def centrifugo_monitor_overview_retrieve(self, hours: int | None = None) -> OverviewStats:
        """
        Get overview statistics

        Returns overview statistics for Centrifugo publishes.
        """
        url = "/cfg/centrifugo/monitor/overview/"
        response = self._client.get(url, params={"hours": hours if hours is not None else None})
        response.raise_for_status()
        return OverviewStats.model_validate(response.json())


    def centrifugo_monitor_publishes_retrieve(self, channel: str | None = None, count: int | None = None, offset: int | None = None, status: str | None = None) -> RecentPublishes:
        """
        Get recent publishes

        Returns a list of recent Centrifugo publishes with their details.
        """
        url = "/cfg/centrifugo/monitor/publishes/"
        response = self._client.get(url, params={"channel": channel if channel is not None else None, "count": count if count is not None else None, "offset": offset if offset is not None else None, "status": status if status is not None else None})
        response.raise_for_status()
        return RecentPublishes.model_validate(response.json())


    def centrifugo_monitor_timeline_retrieve(self, hours: int | None = None, interval: str | None = None) -> list[ChannelList]:
        """
        Get channel statistics

        Returns statistics grouped by channel.
        """
        url = "/cfg/centrifugo/monitor/timeline/"
        response = self._client.get(url, params={"hours": hours if hours is not None else None, "interval": interval if interval is not None else None})
        response.raise_for_status()
        return ChannelList.model_validate(response.json())


