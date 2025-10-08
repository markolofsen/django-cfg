from __future__ import annotations

import httpx

from .models import *


class SyncShopBlogCategoriesAPI:
    """Synchronous API endpoints for Blog - Categories."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def list(self, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None) -> list[PaginatedBlogCategoryList]:
        """
        List categories

        Get a list of all blog categories
        """
        url = "/blog/categories/"
        response = self._client.get(url, params={"ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedBlogCategoryList.model_validate(item) for item in data.get("results", [])]


    def create(self, data: BlogCategoryRequest) -> BlogCategory:
        """
        Create category

        Create a new blog category
        """
        url = "/blog/categories/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return BlogCategory.model_validate(response.json())


    def retrieve(self, slug: str) -> BlogCategory:
        """
        Get category

        Get details of a specific category
        """
        url = f"/blog/categories/{slug}/"
        response = self._client.get(url)
        response.raise_for_status()
        return BlogCategory.model_validate(response.json())


    def update(self, slug: str, data: BlogCategoryRequest) -> BlogCategory:
        """
        Update category

        Update category information
        """
        url = f"/blog/categories/{slug}/"
        response = self._client.put(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return BlogCategory.model_validate(response.json())


    def destroy(self, slug: str) -> None:
        """
        Delete category

        Delete a category
        """
        url = f"/blog/categories/{slug}/"
        response = self._client.delete(url)
        response.raise_for_status()


