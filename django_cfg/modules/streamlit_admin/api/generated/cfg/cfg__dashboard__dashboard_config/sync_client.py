from __future__ import annotations

import httpx

from .models import (
    ConfigData,
)


class SyncCfgDashboardConfigAPI:
    """Synchronous API endpoints for Dashboard - Config."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def dashboard_api_config_config_retrieve(self) -> ConfigData:
        """
        Get configuration data

        Retrieve user's DjangoConfig settings and complete Django settings
        (sanitized)
        """
        url = "/cfg/dashboard/api/config/config/"
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
        return ConfigData.model_validate(response.json())


