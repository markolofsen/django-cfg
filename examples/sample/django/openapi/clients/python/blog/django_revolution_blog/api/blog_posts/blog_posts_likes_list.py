from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.blog_posts_likes_list_status import BlogPostsLikesListStatus
from ...models.blog_posts_likes_list_status import check_blog_posts_likes_list_status
from ...models.paginated_post_like_list import PaginatedPostLikeList
from ...types import UNSET, Unset
from typing import cast
from typing import Union


def _get_kwargs(
    slug: str,
    *,
    author: Union[Unset, int] = UNSET,
    category: Union[Unset, int] = UNSET,
    is_featured: Union[Unset, bool] = UNSET,
    ordering: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = UNSET,
    status: Union[Unset, BlogPostsLikesListStatus] = UNSET,
    tags: Union[Unset, list[int]] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["author"] = author

    params["category"] = category

    params["is_featured"] = is_featured

    params["ordering"] = ordering

    params["page"] = page

    params["page_size"] = page_size

    params["search"] = search

    json_status: Union[Unset, str] = UNSET
    if not isinstance(status, Unset):
        json_status = status

    params["status"] = json_status

    json_tags: Union[Unset, list[int]] = UNSET
    if not isinstance(tags, Unset):
        json_tags = tags

    params["tags"] = json_tags

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/blog/posts/{slug}/likes/".format(
            slug=slug,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[PaginatedPostLikeList]:
    if response.status_code == 200:
        response_200 = PaginatedPostLikeList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[PaginatedPostLikeList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    slug: str,
    *,
    client: AuthenticatedClient,
    author: Union[Unset, int] = UNSET,
    category: Union[Unset, int] = UNSET,
    is_featured: Union[Unset, bool] = UNSET,
    ordering: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = UNSET,
    status: Union[Unset, BlogPostsLikesListStatus] = UNSET,
    tags: Union[Unset, list[int]] = UNSET,
) -> Response[PaginatedPostLikeList]:
    """Get post likes

     Get all likes for a post

    Args:
        slug (str):
        author (Union[Unset, int]):
        category (Union[Unset, int]):
        is_featured (Union[Unset, bool]):
        ordering (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        search (Union[Unset, str]):
        status (Union[Unset, BlogPostsLikesListStatus]):
        tags (Union[Unset, list[int]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedPostLikeList]
    """

    kwargs = _get_kwargs(
        slug=slug,
        author=author,
        category=category,
        is_featured=is_featured,
        ordering=ordering,
        page=page,
        page_size=page_size,
        search=search,
        status=status,
        tags=tags,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    slug: str,
    *,
    client: AuthenticatedClient,
    author: Union[Unset, int] = UNSET,
    category: Union[Unset, int] = UNSET,
    is_featured: Union[Unset, bool] = UNSET,
    ordering: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = UNSET,
    status: Union[Unset, BlogPostsLikesListStatus] = UNSET,
    tags: Union[Unset, list[int]] = UNSET,
) -> Optional[PaginatedPostLikeList]:
    """Get post likes

     Get all likes for a post

    Args:
        slug (str):
        author (Union[Unset, int]):
        category (Union[Unset, int]):
        is_featured (Union[Unset, bool]):
        ordering (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        search (Union[Unset, str]):
        status (Union[Unset, BlogPostsLikesListStatus]):
        tags (Union[Unset, list[int]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedPostLikeList
    """

    return sync_detailed(
        slug=slug,
        client=client,
        author=author,
        category=category,
        is_featured=is_featured,
        ordering=ordering,
        page=page,
        page_size=page_size,
        search=search,
        status=status,
        tags=tags,
    ).parsed


async def asyncio_detailed(
    slug: str,
    *,
    client: AuthenticatedClient,
    author: Union[Unset, int] = UNSET,
    category: Union[Unset, int] = UNSET,
    is_featured: Union[Unset, bool] = UNSET,
    ordering: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = UNSET,
    status: Union[Unset, BlogPostsLikesListStatus] = UNSET,
    tags: Union[Unset, list[int]] = UNSET,
) -> Response[PaginatedPostLikeList]:
    """Get post likes

     Get all likes for a post

    Args:
        slug (str):
        author (Union[Unset, int]):
        category (Union[Unset, int]):
        is_featured (Union[Unset, bool]):
        ordering (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        search (Union[Unset, str]):
        status (Union[Unset, BlogPostsLikesListStatus]):
        tags (Union[Unset, list[int]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedPostLikeList]
    """

    kwargs = _get_kwargs(
        slug=slug,
        author=author,
        category=category,
        is_featured=is_featured,
        ordering=ordering,
        page=page,
        page_size=page_size,
        search=search,
        status=status,
        tags=tags,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    slug: str,
    *,
    client: AuthenticatedClient,
    author: Union[Unset, int] = UNSET,
    category: Union[Unset, int] = UNSET,
    is_featured: Union[Unset, bool] = UNSET,
    ordering: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = UNSET,
    status: Union[Unset, BlogPostsLikesListStatus] = UNSET,
    tags: Union[Unset, list[int]] = UNSET,
) -> Optional[PaginatedPostLikeList]:
    """Get post likes

     Get all likes for a post

    Args:
        slug (str):
        author (Union[Unset, int]):
        category (Union[Unset, int]):
        is_featured (Union[Unset, bool]):
        ordering (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        search (Union[Unset, str]):
        status (Union[Unset, BlogPostsLikesListStatus]):
        tags (Union[Unset, list[int]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedPostLikeList
    """

    return (
        await asyncio_detailed(
            slug=slug,
            client=client,
            author=author,
            category=category,
            is_featured=is_featured,
            ordering=ordering,
            page=page,
            page_size=page_size,
            search=search,
            status=status,
            tags=tags,
        )
    ).parsed
