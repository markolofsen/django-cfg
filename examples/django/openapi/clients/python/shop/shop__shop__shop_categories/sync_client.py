from __future__ import annotations

import httpx

from .models import *


class SyncShopCategoriesAPI:
    """Synchronous API endpoints for Shop - Categories."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def list(self, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None) -> list[PaginatedShopCategoryList]:
        """
        List categories

        Get a list of all shop categories
        """
        url = "/shop/categories/"
        response = self._client.get(url, params={"ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedShopCategoryList.model_validate(item) for item in data.get("results", [])]


    def retrieve(self, slug: str) -> ShopCategory:
        """
        Get category

        Get details of a specific category
        """
        url = f"/shop/categories/{slug}/"
        response = self._client.get(url)
        response.raise_for_status()
        return ShopCategory.model_validate(response.json())


