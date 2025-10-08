from __future__ import annotations

import httpx

from .models import *


class ShopBlogPostsAPI:
    """API endpoints for Blog - Posts."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def list(self, author: int | None = None, category: int | None = None, is_featured: bool | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None, status: str | None = None, tags: list[Any] | None = None) -> list[PaginatedPostListList]:
        """List posts

    Get a paginated list of blog posts"""
        url = "/blog/posts/"
        response = await self._client.get(url, params={"author": author if author is not None else None, "category": category if category is not None else None, "is_featured": is_featured if is_featured is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None, "status": status if status is not None else None, "tags": tags if tags is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedPostListList.model_validate(item) for item in data.get("results", [])]


    async def create(self, data: PostCreateRequest) -> PostCreate:
        """Create post

    Create a new blog post"""
        url = "/blog/posts/"
        response = await self._client.post(url, json=data.model_dump() if data else None)
        response.raise_for_status()
        return PostCreate.model_validate(response.json())


    async def retrieve(self, slug: str) -> PostDetail:
        """Get post

    Get detailed information about a specific post"""
        url = f"/blog/posts/{slug}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return PostDetail.model_validate(response.json())


    async def update(self, slug: str, data: PostUpdateRequest) -> PostUpdate:
        """Update post

    Update post information"""
        url = f"/blog/posts/{slug}/"
        response = await self._client.put(url, json=data.model_dump() if data else None)
        response.raise_for_status()
        return PostUpdate.model_validate(response.json())


    async def destroy(self, slug: str) -> None:
        """Delete post

    Delete a blog post"""
        url = f"/blog/posts/{slug}/"
        response = await self._client.delete(url)
        response.raise_for_status()
        return None


    async def like_create(self, slug: str, data: PostDetailRequest) -> PostDetail:
        """Like/unlike post

    Toggle like status for a post"""
        url = f"/blog/posts/{slug}/like/"
        response = await self._client.post(url, json=data.model_dump() if data else None)
        response.raise_for_status()
        return PostDetail.model_validate(response.json())


    async def likes_list(self, slug: str, author: int | None = None, category: int | None = None, is_featured: bool | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None, status: str | None = None, tags: list[Any] | None = None) -> list[PaginatedPostLikeList]:
        """Get post likes

    Get all likes for a post"""
        url = f"/blog/posts/{slug}/likes/"
        response = await self._client.get(url, params={"author": author if author is not None else None, "category": category if category is not None else None, "is_featured": is_featured if is_featured is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None, "status": status if status is not None else None, "tags": tags if tags is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedPostLikeList.model_validate(item) for item in data.get("results", [])]


    async def featured_retrieve(self) -> PostDetail:
        """Get featured posts

    Get featured blog posts"""
        url = "/blog/posts/featured/"
        response = await self._client.get(url)
        response.raise_for_status()
        return PostDetail.model_validate(response.json())


    async def stats_retrieve(self) -> BlogStats:
        """Get blog statistics

    Get comprehensive blog statistics"""
        url = "/blog/posts/stats/"
        response = await self._client.get(url)
        response.raise_for_status()
        return BlogStats.model_validate(response.json())


