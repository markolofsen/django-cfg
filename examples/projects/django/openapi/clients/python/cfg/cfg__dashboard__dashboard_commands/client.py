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


    async def dashboard_api_commands_help_retrieve(self, id: str) -> CommandHelpResponse:
        """
        Get command help

        Get detailed help text for a specific Django management command
        """
        url = f"/cfg/dashboard/api/commands/{id}/help/"
        response = await self._client.get(url)
        response.raise_for_status()
        return CommandHelpResponse.model_validate(response.json())


    async def dashboard_api_commands_execute_create(self, data: CommandExecuteRequestRequest) -> None:
        """
        Execute command

        Execute a Django management command and stream output in Server-Sent
        Events format
        """
        url = "/cfg/dashboard/api/commands/execute/"
        response = await self._client.post(url, json=data.model_dump())
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


