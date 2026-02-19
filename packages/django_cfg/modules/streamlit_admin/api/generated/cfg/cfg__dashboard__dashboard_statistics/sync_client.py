from __future__ import annotations

import httpx

from .models import (
    AppStatistics,
    StatCard,
    UserStatistics,
)


class SyncCfgDashboardStatisticsAPI:
    """Synchronous API endpoints for Dashboard - Statistics."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def dashboard_api_statistics_apps_list(
        self,
        ordering: str | None = None,
        search: str | None = None,
    ) -> list[AppStatistics]:
        """
        Get application statistics

        Retrieve statistics for all enabled django-cfg applications
        """
        url = "/cfg/dashboard/api/statistics/apps/"
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
        return [AppStatistics.model_validate(item) for item in response.json()]


    def dashboard_api_statistics_cards_list(
        self,
        ordering: str | None = None,
        search: str | None = None,
    ) -> list[StatCard]:
        """
        Get statistics cards

        Retrieve dashboard statistics cards with key metrics
        """
        url = "/cfg/dashboard/api/statistics/cards/"
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
        return [StatCard.model_validate(item) for item in response.json()]


    def dashboard_api_statistics_users_retrieve(self) -> UserStatistics:
        """
        Get user statistics

        Retrieve user-related statistics
        """
        url = "/cfg/dashboard/api/statistics/users/"
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
        return UserStatistics.model_validate(response.json())


