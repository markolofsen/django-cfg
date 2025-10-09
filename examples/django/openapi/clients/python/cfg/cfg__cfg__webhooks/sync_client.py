from __future__ import annotations

import httpx

from .models import *


class SyncCfgWebhooksAPI:
    """Synchronous API endpoints for Webhooks."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def cfg_payments_webhooks_retrieve(self, provider: str) -> WebhookResponse:
        """
        Webhook Endpoint Info

        Get webhook endpoint information for debugging and configuration
        """
        url = f"/cfg/payments/webhooks/{provider}/"
        response = self._client.get(url)
        response.raise_for_status()
        return WebhookResponse.model_validate(response.json())


    def cfg_payments_webhooks_create(self, provider: str, data: WebhookResponseRequest) -> WebhookResponse:
        """
        Process Webhook

        Process incoming webhook from payment provider
        """
        url = f"/cfg/payments/webhooks/{provider}/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return WebhookResponse.model_validate(response.json())


    def cfg_payments_webhooks_health_retrieve(self) -> WebhookHealth:
        """
        Webhook Health Check

        Check webhook service health status and recent activity metrics
        """
        url = "/cfg/payments/webhooks/health/"
        response = self._client.get(url)
        response.raise_for_status()
        return WebhookHealth.model_validate(response.json())


    def cfg_payments_webhooks_providers_retrieve(self) -> SupportedProviders:
        """
        Supported Webhook Providers

        Get list of supported webhook providers with configuration details
        """
        url = "/cfg/payments/webhooks/providers/"
        response = self._client.get(url)
        response.raise_for_status()
        return SupportedProviders.model_validate(response.json())


    def cfg_payments_webhooks_stats_retrieve(self, days: int | None = None) -> WebhookStats:
        """
        Webhook Statistics

        Get webhook processing statistics for a given time period
        """
        url = "/cfg/payments/webhooks/stats/"
        response = self._client.get(url, params={"days": days if days is not None else None})
        response.raise_for_status()
        return WebhookStats.model_validate(response.json())


