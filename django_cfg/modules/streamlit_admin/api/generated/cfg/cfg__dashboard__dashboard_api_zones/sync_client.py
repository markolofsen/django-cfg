from __future__ import annotations

import httpx

from .models import (
    APIZone,
    APIZonesSummary,
)


class SyncCfgDashboardApiZonesAPI:
    """Synchronous API endpoints for Dashboard - API Zones."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def list(self, ordering: str | None = None, search: str | None = None) -> list[APIZone]:
        """
        Get all API zones

        Retrieve all OpenAPI zones/groups with their configuration
        """
        url = "/cfg/dashboard/api/zones/"
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
        return [APIZone.model_validate(item) for item in response.json()]


    def summary_retrieve(self) -> APIZonesSummary:
        """
        Get zones summary

        Retrieve zones summary with statistics
        """
        url = "/cfg/dashboard/api/zones/summary/"
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
        return APIZonesSummary.model_validate(response.json())


