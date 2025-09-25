from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.comment import Comment
from ...models.comment_request import CommentRequest
from typing import cast


def _get_kwargs(
    post_slug: str,
    id: int,
    *,
    body: Union[
        CommentRequest,
        CommentRequest,
        CommentRequest,
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/api/blog/posts/{post_slug}/comments/{id}/".format(
            post_slug=post_slug,
            id=id,
        ),
    }

    if isinstance(body, CommentRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, CommentRequest):
        _kwargs["data"] = body.to_dict()

        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if isinstance(body, CommentRequest):
        _kwargs["files"] = body.to_multipart()

        headers["Content-Type"] = "multipart/form-data"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Comment]:
    if response.status_code == 200:
        response_200 = Comment.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Comment]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    post_slug: str,
    id: int,
    *,
    client: AuthenticatedClient,
    body: Union[
        CommentRequest,
        CommentRequest,
        CommentRequest,
    ],
) -> Response[Comment]:
    """Update comment

     Update comment content

    Args:
        post_slug (str):
        id (int):
        body (CommentRequest): Serializer for blog comments.
        body (CommentRequest): Serializer for blog comments.
        body (CommentRequest): Serializer for blog comments.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Comment]
    """

    kwargs = _get_kwargs(
        post_slug=post_slug,
        id=id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    post_slug: str,
    id: int,
    *,
    client: AuthenticatedClient,
    body: Union[
        CommentRequest,
        CommentRequest,
        CommentRequest,
    ],
) -> Optional[Comment]:
    """Update comment

     Update comment content

    Args:
        post_slug (str):
        id (int):
        body (CommentRequest): Serializer for blog comments.
        body (CommentRequest): Serializer for blog comments.
        body (CommentRequest): Serializer for blog comments.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Comment
    """

    return sync_detailed(
        post_slug=post_slug,
        id=id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    post_slug: str,
    id: int,
    *,
    client: AuthenticatedClient,
    body: Union[
        CommentRequest,
        CommentRequest,
        CommentRequest,
    ],
) -> Response[Comment]:
    """Update comment

     Update comment content

    Args:
        post_slug (str):
        id (int):
        body (CommentRequest): Serializer for blog comments.
        body (CommentRequest): Serializer for blog comments.
        body (CommentRequest): Serializer for blog comments.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Comment]
    """

    kwargs = _get_kwargs(
        post_slug=post_slug,
        id=id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    post_slug: str,
    id: int,
    *,
    client: AuthenticatedClient,
    body: Union[
        CommentRequest,
        CommentRequest,
        CommentRequest,
    ],
) -> Optional[Comment]:
    """Update comment

     Update comment content

    Args:
        post_slug (str):
        id (int):
        body (CommentRequest): Serializer for blog comments.
        body (CommentRequest): Serializer for blog comments.
        body (CommentRequest): Serializer for blog comments.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Comment
    """

    return (
        await asyncio_detailed(
            post_slug=post_slug,
            id=id,
            client=client,
            body=body,
        )
    ).parsed
