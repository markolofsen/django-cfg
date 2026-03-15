from __future__ import annotations

import httpx

from .models import (
    Command,
    CommandExecuteRequestRequest,
    CommandHelpResponse,
    CommandsSummary,
)


class SyncCfgDashboardCommandsAPI:
    """Synchronous API endpoints for Dashboard - Commands."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def dashboard_api_commands_list(
        self,
        ordering: str | None = None,
        search: str | None = None,
    ) -> list[Command]:
        """
        Get all commands

        Retrieve all available Django management commands
        """
        url = "/cfg/dashboard/api/commands/"
        _params = {
            k: v for k, v in {
                "ordering": ordering,
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
        return [Command.model_validate(item) for item in response.json()]


    def dashboard_api_commands_help_retrieve(self, id: str) -> CommandHelpResponse:
        """
        Get command help

        Get detailed help text for a specific Django management command
        """
        url = f"/cfg/dashboard/api/commands/{id}/help/"
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
        return CommandHelpResponse.model_validate(response.json())


    def dashboard_api_commands_execute_create(
        self,
        data: CommandExecuteRequestRequest,
    ) -> None:
        """
        Execute command

        Execute a Django management command and stream output in Server-Sent
        Events format
        """
        url = "/cfg/dashboard/api/commands/execute/"
        response = self._client.post(url, json=data.model_dump(mode="json", exclude_unset=True, exclude_none=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )


    def dashboard_api_commands_summary_retrieve(self) -> CommandsSummary:
        """
        Get commands summary

        Retrieve commands summary with statistics and categorization
        """
        url = "/cfg/dashboard/api/commands/summary/"
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
        return CommandsSummary.model_validate(response.json())


