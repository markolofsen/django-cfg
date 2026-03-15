from __future__ import annotations

import httpx

from .models import (
    PaginatedServiceSummaryList,
    ServiceDetail,
    ServiceMethods,
)


class CfgGrpcServicesAPI:
    """API endpoints for Grpc Services."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def list(
        self,
        hours: int | None = None,
        ordering: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        search: str | None = None,
    ) -> list[PaginatedServiceSummaryList]:
        """
        List all services

        Returns paginated list of all registered gRPC services with basic
        statistics.
        """
        url = "/cfg/grpc/services/"
        _params = {
            k: v for k, v in {
                "hours": hours,
                "ordering": ordering,
                "page": page,
                "page_size": page_size,
                "search": search,
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
        return PaginatedServiceSummaryList.model_validate(response.json())


    async def retrieve(self, id: str, pk: str) -> ServiceDetail:
        """
        Get service details

        Returns detailed information about a specific gRPC service.
        """
        url = f"/cfg/grpc/services/{id}/"
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
        return ServiceDetail.model_validate(response.json())


    async def methods_retrieve(self, id: str, pk: str) -> ServiceMethods:
        """
        Get service methods

        Returns list of methods for a specific service with statistics.
        """
        url = f"/cfg/grpc/services/{id}/methods/"
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
        return ServiceMethods.model_validate(response.json())


