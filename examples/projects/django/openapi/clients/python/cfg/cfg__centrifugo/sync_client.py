from __future__ import annotations

import httpx

from .models import *


class SyncCfgCentrifugoAPI:
    """Synchronous API endpoints for Centrifugo."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def admin_api_monitor_channels_retrieve(self) -> None:
        """
        Get statistics per channel.
        """
        url = "/cfg/centrifugo/admin/api/monitor/channels/"
        response = self._client.get(url)
        response.raise_for_status()


    def monitor_channels_retrieve(self) -> None:
        """
        Get statistics per channel.
        """
        url = "/cfg/centrifugo/monitor/channels/"
        response = self._client.get(url)
        response.raise_for_status()


