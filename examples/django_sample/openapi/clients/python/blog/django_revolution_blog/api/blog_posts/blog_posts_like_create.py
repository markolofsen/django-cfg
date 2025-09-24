from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.post_detail import PostDetail
from ...models.post_detail_request import PostDetailRequest
from typing import cast


def _get_kwargs(
    slug: str,
    *,
    body: Union[
        PostDetailRequest,
        PostDetailRequest,
        PostDetailRequest,
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/blog/posts/{slug}/like/".format(
            slug=slug,
        ),
    }

    if isinstance(body, PostDetailRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, PostDetailRequest):
        _kwargs["data"] = body.to_dict()

        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if isinstance(body, PostDetailRequest):
        _kwargs["files"] = body.to_multipart()

        headers["Content-Type"] = "multipart/form-data"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[PostDetail]:
    if response.status_code == 200:
        response_200 = PostDetail.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[PostDetail]:
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
    body: Union[
        PostDetailRequest,
        PostDetailRequest,
        PostDetailRequest,
    ],
) -> Response[PostDetail]:
    """Like/unlike post

     Toggle like status for a post

    Args:
        slug (str):
        body (PostDetailRequest): Serializer for post detail view.
        body (PostDetailRequest): Serializer for post detail view.
        body (PostDetailRequest): Serializer for post detail view.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostDetail]
    """

    kwargs = _get_kwargs(
        slug=slug,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    slug: str,
    *,
    client: AuthenticatedClient,
    body: Union[
        PostDetailRequest,
        PostDetailRequest,
        PostDetailRequest,
    ],
) -> Optional[PostDetail]:
    """Like/unlike post

     Toggle like status for a post

    Args:
        slug (str):
        body (PostDetailRequest): Serializer for post detail view.
        body (PostDetailRequest): Serializer for post detail view.
        body (PostDetailRequest): Serializer for post detail view.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostDetail
    """

    return sync_detailed(
        slug=slug,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    slug: str,
    *,
    client: AuthenticatedClient,
    body: Union[
        PostDetailRequest,
        PostDetailRequest,
        PostDetailRequest,
    ],
) -> Response[PostDetail]:
    """Like/unlike post

     Toggle like status for a post

    Args:
        slug (str):
        body (PostDetailRequest): Serializer for post detail view.
        body (PostDetailRequest): Serializer for post detail view.
        body (PostDetailRequest): Serializer for post detail view.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostDetail]
    """

    kwargs = _get_kwargs(
        slug=slug,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    slug: str,
    *,
    client: AuthenticatedClient,
    body: Union[
        PostDetailRequest,
        PostDetailRequest,
        PostDetailRequest,
    ],
) -> Optional[PostDetail]:
    """Like/unlike post

     Toggle like status for a post

    Args:
        slug (str):
        body (PostDetailRequest): Serializer for post detail view.
        body (PostDetailRequest): Serializer for post detail view.
        body (PostDetailRequest): Serializer for post detail view.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostDetail
    """

    return (
        await asyncio_detailed(
            slug=slug,
            client=client,
            body=body,
        )
    ).parsed
