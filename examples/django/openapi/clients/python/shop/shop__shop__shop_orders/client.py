from __future__ import annotations

import httpx

from .models import *


class ShopOrdersAPI:
    """API endpoints for Shop - Orders."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def list(self, customer: int | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None, status: str | None = None) -> list[PaginatedOrderListList]:
        """List orders

    Get a list of orders (admin only)"""
        url = "/shop/orders/"
        response = await self._client.get(url, params={"customer": customer if customer is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None, "status": status if status is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedOrderListList.model_validate(item) for item in data.get("results", [])]


    async def retrieve(self, id: int) -> OrderDetail:
        """Get order

    Get details of a specific order"""
        url = f"/shop/orders/{id}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return OrderDetail.model_validate(response.json())


