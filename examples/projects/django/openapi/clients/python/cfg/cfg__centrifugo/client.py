from __future__ import annotations

import httpx

from .models import *


class CfgCentrifugoAPI:
    """API endpoints for Centrifugo."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def monitor_channels_retrieve(self) -> None:
        """
        Get statistics per channel.
        """
        url = "/cfg/centrifugo/monitor/channels/"
        response = await self._client.get(url)
        response.raise_for_status()
        return None


