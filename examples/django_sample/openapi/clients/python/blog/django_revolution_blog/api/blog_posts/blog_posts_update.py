from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.post_update import PostUpdate
from ...models.post_update_request import PostUpdateRequest
from typing import cast


def _get_kwargs(
    slug: str,
    *,
    body: Union[
        PostUpdateRequest,
        PostUpdateRequest,
        PostUpdateRequest,
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/api/blog/posts/{slug}/".format(
            slug=slug,
        ),
    }

    if isinstance(body, PostUpdateRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, PostUpdateRequest):
        _kwargs["data"] = body.to_dict()

        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if isinstance(body, PostUpdateRequest):
        _kwargs["files"] = body.to_multipart()

        headers["Content-Type"] = "multipart/form-data"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[PostUpdate]:
    if response.status_code == 200:
        response_200 = PostUpdate.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[PostUpdate]:
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
        PostUpdateRequest,
        PostUpdateRequest,
        PostUpdateRequest,
    ],
) -> Response[PostUpdate]:
    """Update post

     Update post information

    Args:
        slug (str):
        body (PostUpdateRequest): Serializer for post updates.
        body (PostUpdateRequest): Serializer for post updates.
        body (PostUpdateRequest): Serializer for post updates.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostUpdate]
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
        PostUpdateRequest,
        PostUpdateRequest,
        PostUpdateRequest,
    ],
) -> Optional[PostUpdate]:
    """Update post

     Update post information

    Args:
        slug (str):
        body (PostUpdateRequest): Serializer for post updates.
        body (PostUpdateRequest): Serializer for post updates.
        body (PostUpdateRequest): Serializer for post updates.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostUpdate
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
        PostUpdateRequest,
        PostUpdateRequest,
        PostUpdateRequest,
    ],
) -> Response[PostUpdate]:
    """Update post

     Update post information

    Args:
        slug (str):
        body (PostUpdateRequest): Serializer for post updates.
        body (PostUpdateRequest): Serializer for post updates.
        body (PostUpdateRequest): Serializer for post updates.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostUpdate]
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
        PostUpdateRequest,
        PostUpdateRequest,
        PostUpdateRequest,
    ],
) -> Optional[PostUpdate]:
    """Update post

     Update post information

    Args:
        slug (str):
        body (PostUpdateRequest): Serializer for post updates.
        body (PostUpdateRequest): Serializer for post updates.
        body (PostUpdateRequest): Serializer for post updates.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostUpdate
    """

    return (
        await asyncio_detailed(
            slug=slug,
            client=client,
            body=body,
        )
    ).parsed
