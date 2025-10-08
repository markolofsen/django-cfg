from __future__ import annotations

import httpx

from .models import *


class SyncShopProductsAPI:
    """Synchronous API endpoints for Shop - Products."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def list(self, category: int | None = None, is_digital: bool | None = None, is_featured: bool | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None, status: str | None = None) -> list[PaginatedProductListList]:
        """
        List products

        Get a paginated list of products
        """
        url = "/shop/products/"
        response = self._client.get(url, params={"category": category if category is not None else None, "is_digital": is_digital if is_digital is not None else None, "is_featured": is_featured if is_featured is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None, "status": status if status is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedProductListList.model_validate(item) for item in data.get("results", [])]


    def retrieve(self, slug: str) -> ProductDetail:
        """
        Get product

        Get detailed information about a specific product
        """
        url = f"/shop/products/{slug}/"
        response = self._client.get(url)
        response.raise_for_status()
        return ProductDetail.model_validate(response.json())


    def featured_retrieve(self) -> ProductDetail:
        """
        Get featured products

        Get featured products
        """
        url = "/shop/products/featured/"
        response = self._client.get(url)
        response.raise_for_status()
        return ProductDetail.model_validate(response.json())


    def stats_retrieve(self) -> ShopStats:
        """
        Get shop statistics

        Get comprehensive shop statistics
        """
        url = "/shop/products/stats/"
        response = self._client.get(url)
        response.raise_for_status()
        return ShopStats.model_validate(response.json())


