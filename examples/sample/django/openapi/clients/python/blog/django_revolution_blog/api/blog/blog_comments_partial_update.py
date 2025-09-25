from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.comment import Comment
from ...models.patched_comment_request import PatchedCommentRequest
from typing import cast


def _get_kwargs(
    id: int,
    *,
    body: Union[
        PatchedCommentRequest,
        PatchedCommentRequest,
        PatchedCommentRequest,
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/api/blog/comments/{id}/".format(
            id=id,
        ),
    }

    if isinstance(body, PatchedCommentRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, PatchedCommentRequest):
        _kwargs["data"] = body.to_dict()

        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if isinstance(body, PatchedCommentRequest):
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
    id: int,
    *,
    client: AuthenticatedClient,
    body: Union[
        PatchedCommentRequest,
        PatchedCommentRequest,
        PatchedCommentRequest,
    ],
) -> Response[Comment]:
    """ViewSet for blog comments.

    Args:
        id (int):
        body (PatchedCommentRequest): Serializer for blog comments.
        body (PatchedCommentRequest): Serializer for blog comments.
        body (PatchedCommentRequest): Serializer for blog comments.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Comment]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: int,
    *,
    client: AuthenticatedClient,
    body: Union[
        PatchedCommentRequest,
        PatchedCommentRequest,
        PatchedCommentRequest,
    ],
) -> Optional[Comment]:
    """ViewSet for blog comments.

    Args:
        id (int):
        body (PatchedCommentRequest): Serializer for blog comments.
        body (PatchedCommentRequest): Serializer for blog comments.
        body (PatchedCommentRequest): Serializer for blog comments.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Comment
    """

    return sync_detailed(
        id=id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    id: int,
    *,
    client: AuthenticatedClient,
    body: Union[
        PatchedCommentRequest,
        PatchedCommentRequest,
        PatchedCommentRequest,
    ],
) -> Response[Comment]:
    """ViewSet for blog comments.

    Args:
        id (int):
        body (PatchedCommentRequest): Serializer for blog comments.
        body (PatchedCommentRequest): Serializer for blog comments.
        body (PatchedCommentRequest): Serializer for blog comments.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Comment]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: int,
    *,
    client: AuthenticatedClient,
    body: Union[
        PatchedCommentRequest,
        PatchedCommentRequest,
        PatchedCommentRequest,
    ],
) -> Optional[Comment]:
    """ViewSet for blog comments.

    Args:
        id (int):
        body (PatchedCommentRequest): Serializer for blog comments.
        body (PatchedCommentRequest): Serializer for blog comments.
        body (PatchedCommentRequest): Serializer for blog comments.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Comment
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
