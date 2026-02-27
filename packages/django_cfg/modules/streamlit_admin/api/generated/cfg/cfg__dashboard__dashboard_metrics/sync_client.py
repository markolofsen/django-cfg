from __future__ import annotations

import httpx

from .models import (
    MetricsResponse,
)


class SyncCfgDashboardMetricsAPI:
    """Synchronous API endpoints for Dashboard Metrics."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def dashboard_api_metrics_list(
        self,
        categories: str | None = None,
        force: bool | None = None,
    ) -> list[MetricsResponse]:
        """
        Get all metrics

        Retrieve metrics from all or specific categories. **Available
        Categories:** - `llm_balances` - LLM provider API keys and account
        balances - `system_health` - Database, cache, queue health status -
        `api_stats` - API usage statistics (coming soon) **Query Parameters:** -
        `categories` - Comma-separated list of categories (optional) - `force` -
        Force refresh, bypass cache (default: false)
        """
        url = "/cfg/dashboard/api/metrics/"
        _params = {
            k: v for k, v in {
                "categories": categories,
                "force": force,
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
        return [MetricsResponse.model_validate(item) for item in response.json()]


    def dashboard_api_metrics_llm_balances_retrieve(self, force: bool | None = None) -> None:
        """
        Get LLM balances

        Get LLM provider balances and API key status. **Providers:** - OpenAI -
        API key validation (balance check unavailable) - OpenRouter - Prepaid
        credit balance **Status Levels:** - `ok` - Balance above $10 or API key
        valid - `warning` - Balance between $5-$10 - `critical` - Balance below
        $5 - `error` - API key invalid or request failed
        """
        url = "/cfg/dashboard/api/metrics/llm-balances/"
        _params = {
            k: v for k, v in {
                "force": force,
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


    def dashboard_api_metrics_system_health_retrieve(
        self,
        force: bool | None = None,
    ) -> None:
        """
        Get system health

        Get system component health status. **Components:** - Database -
        PostgreSQL/MySQL connectivity - Cache - Redis/Memcached status - Queue -
        RQ/Celery worker status (if available)
        """
        url = "/cfg/dashboard/api/metrics/system-health/"
        _params = {
            k: v for k, v in {
                "force": force,
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


