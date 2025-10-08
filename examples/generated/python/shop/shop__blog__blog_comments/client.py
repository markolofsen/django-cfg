from __future__ import annotations

import httpx

from .models import *


class ShopBlogCommentsAPI:
    """API endpoints for Blog - Comments."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def list(self, post_slug: str, author: int | None = None, is_approved: bool | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, parent: int | None = None, post: int | None = None) -> list[PaginatedCommentList]:
        """
        List comments

        Get a list of comments
        """
        url = f"/blog/comments/"
        response = await self._client.get(url, params={"author": author if author is not None else None, "is_approved": is_approved if is_approved is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "parent": parent if parent is not None else None, "post": post if post is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedCommentList.model_validate(item) for item in data.get("results", [])]


    async def create(self, post_slug: str, data: CommentRequest) -> Comment:
        """
        Create comment

        Create a new comment
        """
        url = f"/blog/comments/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return Comment.model_validate(response.json())


    async def retrieve(self, id: int) -> Comment:
        """
        Get comment

        Get details of a specific comment
        """
        url = f"/blog/comments/{id}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Comment.model_validate(response.json())


    async def update(self, id: int, data: CommentRequest) -> Comment:
        """
        Update comment

        Update comment content
        """
        url = f"/blog/comments/{id}/"
        response = await self._client.put(url, json=data.model_dump())
        response.raise_for_status()
        return Comment.model_validate(response.json())


    async def partial_update(self, id: int, data: PatchedCommentRequest | None = None) -> Comment:
        """
        Partially update comment

        Partially update comment content
        """
        url = f"/blog/comments/{id}/"
        response = await self._client.patch(url, json=data.model_dump() if data is not None else None)
        response.raise_for_status()
        return Comment.model_validate(response.json())


    async def destroy(self, id: int) -> None:
        """
        Delete comment

        Delete a comment
        """
        url = f"/blog/comments/{id}/"
        response = await self._client.delete(url)
        response.raise_for_status()
        return None


    async def blog_posts_comments_list(self, post_slug: str, author: int | None = None, is_approved: bool | None = None, ordering: str | None = None, page: int | None = None, page_size: int | None = None, parent: int | None = None, post: int | None = None) -> list[PaginatedCommentList]:
        """
        List comments

        Get a list of comments
        """
        url = f"/blog/posts/{post_slug}/comments/"
        response = await self._client.get(url, params={"author": author if author is not None else None, "is_approved": is_approved if is_approved is not None else None, "ordering": ordering if ordering is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "parent": parent if parent is not None else None, "post": post if post is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedCommentList.model_validate(item) for item in data.get("results", [])]


    async def blog_posts_comments_create(self, post_slug: str, data: CommentRequest) -> Comment:
        """
        Create comment

        Create a new comment
        """
        url = f"/blog/posts/{post_slug}/comments/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return Comment.model_validate(response.json())


    async def blog_posts_comments_retrieve(self, id: int, post_slug: str) -> Comment:
        """
        Get comment

        Get details of a specific comment
        """
        url = f"/blog/posts/{post_slug}/comments/{id}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Comment.model_validate(response.json())


    async def blog_posts_comments_update(self, id: int, post_slug: str, data: CommentRequest) -> Comment:
        """
        Update comment

        Update comment content
        """
        url = f"/blog/posts/{post_slug}/comments/{id}/"
        response = await self._client.put(url, json=data.model_dump())
        response.raise_for_status()
        return Comment.model_validate(response.json())


    async def blog_posts_comments_partial_update(self, id: int, post_slug: str, data: PatchedCommentRequest | None = None) -> Comment:
        """
        Partially update comment

        Partially update comment content
        """
        url = f"/blog/posts/{post_slug}/comments/{id}/"
        response = await self._client.patch(url, json=data.model_dump() if data is not None else None)
        response.raise_for_status()
        return Comment.model_validate(response.json())


    async def blog_posts_comments_destroy(self, id: int, post_slug: str) -> None:
        """
        Delete comment

        Delete a comment
        """
        url = f"/blog/posts/{post_slug}/comments/{id}/"
        response = await self._client.delete(url)
        response.raise_for_status()
        return None


