from __future__ import annotations

import httpx

from .models import (
    RQConfig,
    RQHealthCheck,
)


class SyncCfgRqMonitoringAPI:
    """Synchronous API endpoints for RQ Monitoring."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def rq_monitor_config_retrieve(self) -> RQConfig:
        """
        Get RQ configuration

        Returns current RQ configuration from django-cfg.
        """
        url = "/cfg/rq/monitor/config/"
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
        return RQConfig.model_validate(response.json())


    def rq_monitor_health_retrieve(self) -> RQHealthCheck:
        """
        Health check

        Returns RQ cluster health status including worker count and queue
        status.
        """
        url = "/cfg/rq/monitor/health/"
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
        return RQHealthCheck.model_validate(response.json())


    def rq_monitor_metrics_retrieve(self) -> None:
        """
        Prometheus metrics

        Returns Prometheus metrics for RQ queues and workers.
        """
        url = "/cfg/rq/monitor/metrics/"
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


