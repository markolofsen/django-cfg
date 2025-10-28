from __future__ import annotations

import httpx

from .models import *


class SyncCfgCentrifugoAdminApiAPI:
    """Synchronous API endpoints for Centrifugo Admin API."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def centrifugo_server_auth_token_create(self) -> None:
        """
        Get connection token for dashboard

        Returns JWT token and config for WebSocket connection to Centrifugo.
        """
        url = "/cfg/centrifugo/server/auth/token/"
        response = self._client.post(url)
        response.raise_for_status()


    def centrifugo_server_channels_create(self, data: CentrifugoChannelsRequestRequest) -> CentrifugoChannelsResponse:
        """
        List active channels

        Returns list of active channels with optional pattern filter.
        """
        url = "/cfg/centrifugo/server/channels/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return CentrifugoChannelsResponse.model_validate(response.json())


    def centrifugo_server_history_create(self, data: CentrifugoHistoryRequestRequest) -> CentrifugoHistoryResponse:
        """
        Get channel history

        Returns message history for a channel.
        """
        url = "/cfg/centrifugo/server/history/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return CentrifugoHistoryResponse.model_validate(response.json())


    def centrifugo_server_info_create(self) -> CentrifugoInfoResponse:
        """
        Get Centrifugo server info

        Returns server information including node count, version, and uptime.
        """
        url = "/cfg/centrifugo/server/info/"
        response = self._client.post(url)
        response.raise_for_status()
        return CentrifugoInfoResponse.model_validate(response.json())


    def centrifugo_server_presence_create(self, data: CentrifugoPresenceRequestRequest) -> CentrifugoPresenceResponse:
        """
        Get channel presence

        Returns list of clients currently subscribed to a channel.
        """
        url = "/cfg/centrifugo/server/presence/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return CentrifugoPresenceResponse.model_validate(response.json())


    def centrifugo_server_presence_stats_create(self, data: CentrifugoPresenceStatsRequestRequest) -> CentrifugoPresenceStatsResponse:
        """
        Get channel presence statistics

        Returns quick statistics about channel presence (num_clients,
        num_users).
        """
        url = "/cfg/centrifugo/server/presence-stats/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return CentrifugoPresenceStatsResponse.model_validate(response.json())


