from __future__ import annotations

import httpx

from .models import *


class SyncCfgCentrifugoAPI:
    """Synchronous API endpoints for Centrifugo."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def monitor_channels_retrieve(self) -> None:
        """
        Get statistics per channel.
        """
        url = "/cfg/centrifugo/monitor/channels/"
        response = self._client.get(url)
        response.raise_for_status()


