from __future__ import annotations

import httpx

from .models import *


class CfgWebhooksAPI:
    """API endpoints for Webhooks."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def payments_webhooks_retrieve(self, provider: str) -> WebhookResponse:
        """
        Webhook Endpoint Info

        Get webhook endpoint information for debugging and configuration
        """
        url = f"/payments/webhooks/{provider}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return WebhookResponse.model_validate(response.json())


    async def payments_webhooks_create(self, provider: str, data: WebhookResponseRequest) -> WebhookResponse:
        """
        Process Webhook

        Process incoming webhook from payment provider
        """
        url = f"/payments/webhooks/{provider}/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return WebhookResponse.model_validate(response.json())


    async def payments_webhooks_health_retrieve(self) -> WebhookHealth:
        """
        Webhook Health Check

        Check webhook service health status and recent activity metrics
        """
        url = "/payments/webhooks/health/"
        response = await self._client.get(url)
        response.raise_for_status()
        return WebhookHealth.model_validate(response.json())


    async def payments_webhooks_providers_retrieve(self) -> SupportedProviders:
        """
        Supported Webhook Providers

        Get list of supported webhook providers with configuration details
        """
        url = "/payments/webhooks/providers/"
        response = await self._client.get(url)
        response.raise_for_status()
        return SupportedProviders.model_validate(response.json())


    async def payments_webhooks_stats_retrieve(self, days: int | None = None) -> WebhookStats:
        """
        Webhook Statistics

        Get webhook processing statistics for a given time period
        """
        url = "/payments/webhooks/stats/"
        response = await self._client.get(url, params={"days": days if days is not None else None})
        response.raise_for_status()
        return WebhookStats.model_validate(response.json())


