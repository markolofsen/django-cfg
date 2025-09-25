from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.unsubscribe import Unsubscribe
from ...models.unsubscribe_request import UnsubscribeRequest
from typing import cast


def _get_kwargs(
    *,
    body: Union[
        UnsubscribeRequest,
        UnsubscribeRequest,
        UnsubscribeRequest,
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/api/newsletter/unsubscribe/",
    }

    if isinstance(body, UnsubscribeRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, UnsubscribeRequest):
        _kwargs["data"] = body.to_dict()

        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if isinstance(body, UnsubscribeRequest):
        _kwargs["files"] = body.to_multipart()

        headers["Content-Type"] = "multipart/form-data"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Unsubscribe]:
    if response.status_code == 200:
        response_200 = Unsubscribe.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Unsubscribe]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: Union[
        UnsubscribeRequest,
        UnsubscribeRequest,
        UnsubscribeRequest,
    ],
) -> Response[Unsubscribe]:
    """Handle newsletter unsubscriptions.

    Args:
        body (UnsubscribeRequest): Simple serializer for unsubscribe.
        body (UnsubscribeRequest): Simple serializer for unsubscribe.
        body (UnsubscribeRequest): Simple serializer for unsubscribe.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Unsubscribe]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: Union[
        UnsubscribeRequest,
        UnsubscribeRequest,
        UnsubscribeRequest,
    ],
) -> Optional[Unsubscribe]:
    """Handle newsletter unsubscriptions.

    Args:
        body (UnsubscribeRequest): Simple serializer for unsubscribe.
        body (UnsubscribeRequest): Simple serializer for unsubscribe.
        body (UnsubscribeRequest): Simple serializer for unsubscribe.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Unsubscribe
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: Union[
        UnsubscribeRequest,
        UnsubscribeRequest,
        UnsubscribeRequest,
    ],
) -> Response[Unsubscribe]:
    """Handle newsletter unsubscriptions.

    Args:
        body (UnsubscribeRequest): Simple serializer for unsubscribe.
        body (UnsubscribeRequest): Simple serializer for unsubscribe.
        body (UnsubscribeRequest): Simple serializer for unsubscribe.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Unsubscribe]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: Union[
        UnsubscribeRequest,
        UnsubscribeRequest,
        UnsubscribeRequest,
    ],
) -> Optional[Unsubscribe]:
    """Handle newsletter unsubscriptions.

    Args:
        body (UnsubscribeRequest): Simple serializer for unsubscribe.
        body (UnsubscribeRequest): Simple serializer for unsubscribe.
        body (UnsubscribeRequest): Simple serializer for unsubscribe.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Unsubscribe
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
