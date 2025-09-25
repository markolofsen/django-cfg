from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.newsletter_campaigns_send_create_response_200 import NewsletterCampaignsSendCreateResponse200
from ...models.newsletter_campaigns_send_create_response_400 import NewsletterCampaignsSendCreateResponse400
from ...models.newsletter_campaigns_send_create_response_404 import NewsletterCampaignsSendCreateResponse404
from ...models.send_campaign_request import SendCampaignRequest
from typing import cast


def _get_kwargs(
    *,
    body: Union[
        SendCampaignRequest,
        SendCampaignRequest,
        SendCampaignRequest,
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/newsletter/campaigns/send/",
    }

    if isinstance(body, SendCampaignRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, SendCampaignRequest):
        _kwargs["data"] = body.to_dict()

        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if isinstance(body, SendCampaignRequest):
        _kwargs["files"] = body.to_multipart()

        headers["Content-Type"] = "multipart/form-data"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        NewsletterCampaignsSendCreateResponse200,
        NewsletterCampaignsSendCreateResponse400,
        NewsletterCampaignsSendCreateResponse404,
    ]
]:
    if response.status_code == 200:
        response_200 = NewsletterCampaignsSendCreateResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = NewsletterCampaignsSendCreateResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 404:
        response_404 = NewsletterCampaignsSendCreateResponse404.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        NewsletterCampaignsSendCreateResponse200,
        NewsletterCampaignsSendCreateResponse400,
        NewsletterCampaignsSendCreateResponse404,
    ]
]:
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
        SendCampaignRequest,
        SendCampaignRequest,
        SendCampaignRequest,
    ],
) -> Response[
    Union[
        NewsletterCampaignsSendCreateResponse200,
        NewsletterCampaignsSendCreateResponse400,
        NewsletterCampaignsSendCreateResponse404,
    ]
]:
    """Send Newsletter Campaign

     Send a newsletter campaign to all subscribers.

    Args:
        body (SendCampaignRequest): Simple serializer for sending campaign.
        body (SendCampaignRequest): Simple serializer for sending campaign.
        body (SendCampaignRequest): Simple serializer for sending campaign.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[NewsletterCampaignsSendCreateResponse200, NewsletterCampaignsSendCreateResponse400, NewsletterCampaignsSendCreateResponse404]]
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
        SendCampaignRequest,
        SendCampaignRequest,
        SendCampaignRequest,
    ],
) -> Optional[
    Union[
        NewsletterCampaignsSendCreateResponse200,
        NewsletterCampaignsSendCreateResponse400,
        NewsletterCampaignsSendCreateResponse404,
    ]
]:
    """Send Newsletter Campaign

     Send a newsletter campaign to all subscribers.

    Args:
        body (SendCampaignRequest): Simple serializer for sending campaign.
        body (SendCampaignRequest): Simple serializer for sending campaign.
        body (SendCampaignRequest): Simple serializer for sending campaign.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[NewsletterCampaignsSendCreateResponse200, NewsletterCampaignsSendCreateResponse400, NewsletterCampaignsSendCreateResponse404]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: Union[
        SendCampaignRequest,
        SendCampaignRequest,
        SendCampaignRequest,
    ],
) -> Response[
    Union[
        NewsletterCampaignsSendCreateResponse200,
        NewsletterCampaignsSendCreateResponse400,
        NewsletterCampaignsSendCreateResponse404,
    ]
]:
    """Send Newsletter Campaign

     Send a newsletter campaign to all subscribers.

    Args:
        body (SendCampaignRequest): Simple serializer for sending campaign.
        body (SendCampaignRequest): Simple serializer for sending campaign.
        body (SendCampaignRequest): Simple serializer for sending campaign.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[NewsletterCampaignsSendCreateResponse200, NewsletterCampaignsSendCreateResponse400, NewsletterCampaignsSendCreateResponse404]]
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
        SendCampaignRequest,
        SendCampaignRequest,
        SendCampaignRequest,
    ],
) -> Optional[
    Union[
        NewsletterCampaignsSendCreateResponse200,
        NewsletterCampaignsSendCreateResponse400,
        NewsletterCampaignsSendCreateResponse404,
    ]
]:
    """Send Newsletter Campaign

     Send a newsletter campaign to all subscribers.

    Args:
        body (SendCampaignRequest): Simple serializer for sending campaign.
        body (SendCampaignRequest): Simple serializer for sending campaign.
        body (SendCampaignRequest): Simple serializer for sending campaign.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[NewsletterCampaignsSendCreateResponse200, NewsletterCampaignsSendCreateResponse400, NewsletterCampaignsSendCreateResponse404]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
