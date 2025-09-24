from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.comment import Comment
from typing import cast


def _get_kwargs(
    post_slug: str,
    id: int,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/blog/posts/{post_slug}/comments/{id}/".format(
            post_slug=post_slug,
            id=id,
        ),
    }

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
) -> Response[Comment]:
    """Get comment

     Get details of a specific comment

    Args:
        post_slug (str):
        id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Comment]
    """

    kwargs = _get_kwargs(
        post_slug=post_slug,
        id=id,
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
) -> Optional[Comment]:
    """Get comment

     Get details of a specific comment

    Args:
        post_slug (str):
        id (int):

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
    ).parsed


async def asyncio_detailed(
    post_slug: str,
    id: int,
    *,
    client: AuthenticatedClient,
) -> Response[Comment]:
    """Get comment

     Get details of a specific comment

    Args:
        post_slug (str):
        id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Comment]
    """

    kwargs = _get_kwargs(
        post_slug=post_slug,
        id=id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    post_slug: str,
    id: int,
    *,
    client: AuthenticatedClient,
) -> Optional[Comment]:
    """Get comment

     Get details of a specific comment

    Args:
        post_slug (str):
        id (int):

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
        )
    ).parsed
