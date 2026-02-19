from __future__ import annotations

import httpx

from .models import (
    GRPCConfig,
    GRPCServerInfo,
)


class SyncCfgGrpcConfigurationAPI:
    """Synchronous API endpoints for Grpc Configuration."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def grpc_config_config_retrieve(self) -> GRPCConfig:
        """
        Get gRPC configuration

        Returns current gRPC server configuration from Django settings.
        """
        url = "/cfg/grpc/config/config/"
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
        return GRPCConfig.model_validate(response.json())


    def grpc_config_server_info_retrieve(self) -> GRPCServerInfo:
        """
        Get server information

        Returns detailed information about gRPC server, services, and runtime
        statistics.
        """
        url = "/cfg/grpc/config/server-info/"
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
        return GRPCServerInfo.model_validate(response.json())


