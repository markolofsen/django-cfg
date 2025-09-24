from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.newsletter_subscribe_create_response_201 import NewsletterSubscribeCreateResponse201
from ...models.newsletter_subscribe_create_response_400 import NewsletterSubscribeCreateResponse400
from ...models.subscribe_request import SubscribeRequest
from typing import cast


def _get_kwargs(
    *,
    body: Union[
        SubscribeRequest,
        SubscribeRequest,
        SubscribeRequest,
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/newsletter/subscribe/",
    }

    if isinstance(body, SubscribeRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, SubscribeRequest):
        _kwargs["data"] = body.to_dict()

        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if isinstance(body, SubscribeRequest):
        _kwargs["files"] = body.to_multipart()

        headers["Content-Type"] = "multipart/form-data"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[NewsletterSubscribeCreateResponse201, NewsletterSubscribeCreateResponse400]]:
    if response.status_code == 201:
        response_201 = NewsletterSubscribeCreateResponse201.from_dict(response.json())

        return response_201

    if response.status_code == 400:
        response_400 = NewsletterSubscribeCreateResponse400.from_dict(response.json())

        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[NewsletterSubscribeCreateResponse201, NewsletterSubscribeCreateResponse400]]:
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
        SubscribeRequest,
        SubscribeRequest,
        SubscribeRequest,
    ],
) -> Response[Union[NewsletterSubscribeCreateResponse201, NewsletterSubscribeCreateResponse400]]:
    """Subscribe to Newsletter

     Subscribe an email address to a newsletter.

    Args:
        body (SubscribeRequest): Simple serializer for newsletter subscription.
        body (SubscribeRequest): Simple serializer for newsletter subscription.
        body (SubscribeRequest): Simple serializer for newsletter subscription.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[NewsletterSubscribeCreateResponse201, NewsletterSubscribeCreateResponse400]]
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
        SubscribeRequest,
        SubscribeRequest,
        SubscribeRequest,
    ],
) -> Optional[Union[NewsletterSubscribeCreateResponse201, NewsletterSubscribeCreateResponse400]]:
    """Subscribe to Newsletter

     Subscribe an email address to a newsletter.

    Args:
        body (SubscribeRequest): Simple serializer for newsletter subscription.
        body (SubscribeRequest): Simple serializer for newsletter subscription.
        body (SubscribeRequest): Simple serializer for newsletter subscription.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[NewsletterSubscribeCreateResponse201, NewsletterSubscribeCreateResponse400]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: Union[
        SubscribeRequest,
        SubscribeRequest,
        SubscribeRequest,
    ],
) -> Response[Union[NewsletterSubscribeCreateResponse201, NewsletterSubscribeCreateResponse400]]:
    """Subscribe to Newsletter

     Subscribe an email address to a newsletter.

    Args:
        body (SubscribeRequest): Simple serializer for newsletter subscription.
        body (SubscribeRequest): Simple serializer for newsletter subscription.
        body (SubscribeRequest): Simple serializer for newsletter subscription.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[NewsletterSubscribeCreateResponse201, NewsletterSubscribeCreateResponse400]]
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
        SubscribeRequest,
        SubscribeRequest,
        SubscribeRequest,
    ],
) -> Optional[Union[NewsletterSubscribeCreateResponse201, NewsletterSubscribeCreateResponse400]]:
    """Subscribe to Newsletter

     Subscribe an email address to a newsletter.

    Args:
        body (SubscribeRequest): Simple serializer for newsletter subscription.
        body (SubscribeRequest): Simple serializer for newsletter subscription.
        body (SubscribeRequest): Simple serializer for newsletter subscription.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[NewsletterSubscribeCreateResponse201, NewsletterSubscribeCreateResponse400]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
