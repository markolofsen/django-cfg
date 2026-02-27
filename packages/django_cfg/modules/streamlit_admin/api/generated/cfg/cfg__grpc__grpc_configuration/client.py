from __future__ import annotations

import httpx

from .models import (
    GRPCConfig,
    GRPCServerInfo,
)


class CfgGrpcConfigurationAPI:
    """API endpoints for Grpc Configuration."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def grpc_config_config_retrieve(self) -> GRPCConfig:
        """
        Get gRPC configuration

        Returns current gRPC server configuration from Django settings.
        """
        url = "/cfg/grpc/config/config/"
        response = await self._client.get(url)
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


    async def grpc_config_server_info_retrieve(self) -> GRPCServerInfo:
        """
        Get server information

        Returns detailed information about gRPC server, services, and runtime
        statistics.
        """
        url = "/cfg/grpc/config/server-info/"
        response = await self._client.get(url)
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


