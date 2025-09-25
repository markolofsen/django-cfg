from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.subscription_create import SubscriptionCreate
from ...models.subscription_create_request import SubscriptionCreateRequest
from typing import cast


def _get_kwargs(
    *,
    body: Union[
        SubscriptionCreateRequest,
        SubscriptionCreateRequest,
        SubscriptionCreateRequest,
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/payments/subscription/create/",
    }

    if isinstance(body, SubscriptionCreateRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, SubscriptionCreateRequest):
        _kwargs["data"] = body.to_dict()

        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if isinstance(body, SubscriptionCreateRequest):
        _kwargs["files"] = body.to_multipart()

        headers["Content-Type"] = "multipart/form-data"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[SubscriptionCreate]:
    if response.status_code == 201:
        response_201 = SubscriptionCreate.from_dict(response.json())

        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[SubscriptionCreate]:
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
        SubscriptionCreateRequest,
        SubscriptionCreateRequest,
        SubscriptionCreateRequest,
    ],
) -> Response[SubscriptionCreate]:
    """Generic view to create subscription.

    Args:
        body (SubscriptionCreateRequest): Create subscription request.
        body (SubscriptionCreateRequest): Create subscription request.
        body (SubscriptionCreateRequest): Create subscription request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SubscriptionCreate]
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
        SubscriptionCreateRequest,
        SubscriptionCreateRequest,
        SubscriptionCreateRequest,
    ],
) -> Optional[SubscriptionCreate]:
    """Generic view to create subscription.

    Args:
        body (SubscriptionCreateRequest): Create subscription request.
        body (SubscriptionCreateRequest): Create subscription request.
        body (SubscriptionCreateRequest): Create subscription request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SubscriptionCreate
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: Union[
        SubscriptionCreateRequest,
        SubscriptionCreateRequest,
        SubscriptionCreateRequest,
    ],
) -> Response[SubscriptionCreate]:
    """Generic view to create subscription.

    Args:
        body (SubscriptionCreateRequest): Create subscription request.
        body (SubscriptionCreateRequest): Create subscription request.
        body (SubscriptionCreateRequest): Create subscription request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SubscriptionCreate]
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
        SubscriptionCreateRequest,
        SubscriptionCreateRequest,
        SubscriptionCreateRequest,
    ],
) -> Optional[SubscriptionCreate]:
    """Generic view to create subscription.

    Args:
        body (SubscriptionCreateRequest): Create subscription request.
        body (SubscriptionCreateRequest): Create subscription request.
        body (SubscriptionCreateRequest): Create subscription request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SubscriptionCreate
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
