from __future__ import annotations

import httpx

from .models import *


class CfgDashboardCommandsAPI:
    """API endpoints for Dashboard - Commands."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def dashboard_api_commands_list(self) -> None:
        """
        Get all commands

        Retrieve all available Django management commands
        """
        url = "/cfg/dashboard/api/commands/"
        response = await self._client.get(url)
        response.raise_for_status()
        return None


    async def dashboard_api_commands_summary_retrieve(self) -> CommandsSummary:
        """
        Get commands summary

        Retrieve commands summary with statistics and categorization
        """
        url = "/cfg/dashboard/api/commands/summary/"
        response = await self._client.get(url)
        response.raise_for_status()
        return CommandsSummary.model_validate(response.json())


