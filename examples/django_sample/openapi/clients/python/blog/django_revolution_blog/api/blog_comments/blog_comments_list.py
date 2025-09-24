from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.paginated_comment_list import PaginatedCommentList
from ...types import UNSET, Unset
from typing import cast
from typing import Union


def _get_kwargs(
    *,
    author: Union[Unset, int] = UNSET,
    is_approved: Union[Unset, bool] = UNSET,
    ordering: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    parent: Union[Unset, int] = UNSET,
    post: Union[Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["author"] = author

    params["is_approved"] = is_approved

    params["ordering"] = ordering

    params["page"] = page

    params["page_size"] = page_size

    params["parent"] = parent

    params["post"] = post

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/blog/comments/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[PaginatedCommentList]:
    if response.status_code == 200:
        response_200 = PaginatedCommentList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[PaginatedCommentList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    author: Union[Unset, int] = UNSET,
    is_approved: Union[Unset, bool] = UNSET,
    ordering: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    parent: Union[Unset, int] = UNSET,
    post: Union[Unset, int] = UNSET,
) -> Response[PaginatedCommentList]:
    """List comments

     Get a list of comments

    Args:
        author (Union[Unset, int]):
        is_approved (Union[Unset, bool]):
        ordering (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        parent (Union[Unset, int]):
        post (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedCommentList]
    """

    kwargs = _get_kwargs(
        author=author,
        is_approved=is_approved,
        ordering=ordering,
        page=page,
        page_size=page_size,
        parent=parent,
        post=post,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    author: Union[Unset, int] = UNSET,
    is_approved: Union[Unset, bool] = UNSET,
    ordering: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    parent: Union[Unset, int] = UNSET,
    post: Union[Unset, int] = UNSET,
) -> Optional[PaginatedCommentList]:
    """List comments

     Get a list of comments

    Args:
        author (Union[Unset, int]):
        is_approved (Union[Unset, bool]):
        ordering (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        parent (Union[Unset, int]):
        post (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedCommentList
    """

    return sync_detailed(
        client=client,
        author=author,
        is_approved=is_approved,
        ordering=ordering,
        page=page,
        page_size=page_size,
        parent=parent,
        post=post,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    author: Union[Unset, int] = UNSET,
    is_approved: Union[Unset, bool] = UNSET,
    ordering: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    parent: Union[Unset, int] = UNSET,
    post: Union[Unset, int] = UNSET,
) -> Response[PaginatedCommentList]:
    """List comments

     Get a list of comments

    Args:
        author (Union[Unset, int]):
        is_approved (Union[Unset, bool]):
        ordering (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        parent (Union[Unset, int]):
        post (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedCommentList]
    """

    kwargs = _get_kwargs(
        author=author,
        is_approved=is_approved,
        ordering=ordering,
        page=page,
        page_size=page_size,
        parent=parent,
        post=post,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    author: Union[Unset, int] = UNSET,
    is_approved: Union[Unset, bool] = UNSET,
    ordering: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    parent: Union[Unset, int] = UNSET,
    post: Union[Unset, int] = UNSET,
) -> Optional[PaginatedCommentList]:
    """List comments

     Get a list of comments

    Args:
        author (Union[Unset, int]):
        is_approved (Union[Unset, bool]):
        ordering (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        parent (Union[Unset, int]):
        post (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedCommentList
    """

    return (
        await asyncio_detailed(
            client=client,
            author=author,
            is_approved=is_approved,
            ordering=ordering,
            page=page,
            page_size=page_size,
            parent=parent,
            post=post,
        )
    ).parsed
