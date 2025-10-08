from __future__ import annotations

import httpx

from .models import *


class SyncShopBlogAPI:
    """Synchronous API endpoints for Blog."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def categories_partial_update(self, slug: str, data: PatchedBlogCategoryRequest | None = None) -> BlogCategory:
        """
        ViewSet for blog categories.
        """
        url = f"/blog/categories/{slug}/"
        response = self._client.patch(url, json=data.model_dump(exclude_unset=True) if data is not None else None)
        response.raise_for_status()
        return BlogCategory.model_validate(response.json())


    def posts_partial_update(self, slug: str, data: PatchedPostUpdateRequest | None = None) -> PostUpdate:
        """
        ViewSet for blog posts.
        """
        url = f"/blog/posts/{slug}/"
        response = self._client.patch(url, json=data.model_dump(exclude_unset=True) if data is not None else None)
        response.raise_for_status()
        return PostUpdate.model_validate(response.json())


    def tags_retrieve(self, slug: str) -> Tag:
        """
        ViewSet for blog tags.
        """
        url = f"/blog/tags/{slug}/"
        response = self._client.get(url)
        response.raise_for_status()
        return Tag.model_validate(response.json())


    def tags_update(self, slug: str, data: TagRequest) -> Tag:
        """
        ViewSet for blog tags.
        """
        url = f"/blog/tags/{slug}/"
        response = self._client.put(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return Tag.model_validate(response.json())


    def tags_partial_update(self, slug: str, data: PatchedTagRequest | None = None) -> Tag:
        """
        ViewSet for blog tags.
        """
        url = f"/blog/tags/{slug}/"
        response = self._client.patch(url, json=data.model_dump(exclude_unset=True) if data is not None else None)
        response.raise_for_status()
        return Tag.model_validate(response.json())


    def tags_destroy(self, slug: str) -> None:
        """
        ViewSet for blog tags.
        """
        url = f"/blog/tags/{slug}/"
        response = self._client.delete(url)
        response.raise_for_status()


