from __future__ import annotations

import httpx

from .models import (
    ApiKey,
    ApiKeyStats,
    PaginatedApiKeyList,
)


class CfgGrpcApiKeysAPI:
    """API endpoints for Grpc Api Keys."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def list(
        self,
        is_active: bool | None = None,
        ordering: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        search: str | None = None,
        user_id: int | None = None,
    ) -> list[PaginatedApiKeyList]:
        """
        List API keys

        Returns a list of all API keys with their details. Uses standard DRF
        pagination.
        """
        url = "/cfg/grpc/api-keys/"
        _params = {
            k: v for k, v in {
                "is_active": is_active,
                "ordering": ordering,
                "page": page,
                "page_size": page_size,
                "search": search,
                "user_id": user_id,
            }.items() if v is not None
        }
        response = await self._client.get(url, params=_params)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return PaginatedApiKeyList.model_validate(response.json())


    async def retrieve(self, id: int) -> ApiKey:
        """
        Get API key details

        Returns detailed information about a specific API key.
        """
        url = f"/cfg/grpc/api-keys/{id}/"
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
        return ApiKey.model_validate(response.json())


    async def stats_retrieve(self) -> ApiKeyStats:
        """
        Get API keys statistics

        Returns overall statistics about API keys usage.
        """
        url = "/cfg/grpc/api-keys/stats/"
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
        return ApiKeyStats.model_validate(response.json())


