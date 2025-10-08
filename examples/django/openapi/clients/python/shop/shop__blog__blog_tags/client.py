from __future__ import annotations

import httpx

from .models import *


class ShopBlogTagsAPI:
    """API endpoints for Blog - Tags."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def list(self, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None) -> list[PaginatedTagList]:
        """List tags

    Get a list of all blog tags"""
        url = "/blog/tags/"
        response = await self._client.get(url, params={"ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedTagList.model_validate(item) for item in data.get("results", [])]


    async def create(self, data: TagRequest) -> Tag:
        """Create tag

    Create a new blog tag"""
        url = "/blog/tags/"
        response = await self._client.post(url, json=data.model_dump() if data else None)
        response.raise_for_status()
        return Tag.model_validate(response.json())


