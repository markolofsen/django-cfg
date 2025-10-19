from __future__ import annotations

import httpx

from .models import *


class SyncTradingTradingAPI:
    """Synchronous API endpoints for Trading."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def orders_list(self, page: int | None = None, page_size: int | None = None) -> list[PaginatedOrderList]:
        """
        List orders

        ViewSet for trading orders.
        """
        url = "/api/trading/orders/"
        response = self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedOrderList.model_validate(item) for item in data.get("results", [])]


    def orders_create(self, data: OrderCreateRequest) -> OrderCreate:
        """
        Create order

        ViewSet for trading orders.
        """
        url = "/api/trading/orders/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return OrderCreate.model_validate(response.json())


    def orders_retrieve(self, id: int) -> Order:
        """
        Get order

        ViewSet for trading orders.
        """
        url = f"/api/trading/orders/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return Order.model_validate(response.json())


    def orders_update(self, id: int, data: OrderRequest) -> Order:
        """
        ViewSet for trading orders.
        """
        url = f"/api/trading/orders/{id}/"
        response = self._client.put(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return Order.model_validate(response.json())


    def orders_partial_update(self, id: int, data: PatchedOrderRequest | None = None) -> Order:
        """
        ViewSet for trading orders.
        """
        url = f"/api/trading/orders/{id}/"
        response = self._client.patch(url, json=data.model_dump(exclude_unset=True) if data is not None else None)
        response.raise_for_status()
        return Order.model_validate(response.json())


    def orders_destroy(self, id: int) -> None:
        """
        ViewSet for trading orders.
        """
        url = f"/api/trading/orders/{id}/"
        response = self._client.delete(url)
        response.raise_for_status()


    def portfolios_list(self, page: int | None = None, page_size: int | None = None) -> list[PaginatedPortfolioList]:
        """
        List portfolios

        ViewSet for trading portfolios.
        """
        url = "/api/trading/portfolios/"
        response = self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedPortfolioList.model_validate(item) for item in data.get("results", [])]


    def portfolios_retrieve(self, id: int) -> Portfolio:
        """
        Get portfolio

        ViewSet for trading portfolios.
        """
        url = f"/api/trading/portfolios/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return Portfolio.model_validate(response.json())


    def portfolios_me_retrieve(self) -> Portfolio:
        """
        Get my portfolio

        Get current user's portfolio.
        """
        url = "/api/trading/portfolios/me/"
        response = self._client.get(url)
        response.raise_for_status()
        return Portfolio.model_validate(response.json())


    def portfolios_stats_retrieve(self) -> PortfolioStats:
        """
        Get portfolio statistics

        Get portfolio statistics.
        """
        url = "/api/trading/portfolios/stats/"
        response = self._client.get(url)
        response.raise_for_status()
        return PortfolioStats.model_validate(response.json())


