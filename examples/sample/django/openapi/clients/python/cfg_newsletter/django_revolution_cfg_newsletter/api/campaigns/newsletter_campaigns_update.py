from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.newsletter_campaign import NewsletterCampaign
from ...models.newsletter_campaign_request import NewsletterCampaignRequest
from typing import cast


def _get_kwargs(
    id: int,
    *,
    body: Union[
        NewsletterCampaignRequest,
        NewsletterCampaignRequest,
        NewsletterCampaignRequest,
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/api/newsletter/campaigns/{id}/".format(
            id=id,
        ),
    }

    if isinstance(body, NewsletterCampaignRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, NewsletterCampaignRequest):
        _kwargs["data"] = body.to_dict()

        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if isinstance(body, NewsletterCampaignRequest):
        _kwargs["files"] = body.to_multipart()

        headers["Content-Type"] = "multipart/form-data"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[NewsletterCampaign]:
    if response.status_code == 200:
        response_200 = NewsletterCampaign.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[NewsletterCampaign]:
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
        NewsletterCampaignRequest,
        NewsletterCampaignRequest,
        NewsletterCampaignRequest,
    ],
) -> Response[NewsletterCampaign]:
    """Update Campaign

     Update a newsletter campaign.

    Args:
        id (int):
        body (NewsletterCampaignRequest): Serializer for NewsletterCampaign model.
        body (NewsletterCampaignRequest): Serializer for NewsletterCampaign model.
        body (NewsletterCampaignRequest): Serializer for NewsletterCampaign model.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[NewsletterCampaign]
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
        NewsletterCampaignRequest,
        NewsletterCampaignRequest,
        NewsletterCampaignRequest,
    ],
) -> Optional[NewsletterCampaign]:
    """Update Campaign

     Update a newsletter campaign.

    Args:
        id (int):
        body (NewsletterCampaignRequest): Serializer for NewsletterCampaign model.
        body (NewsletterCampaignRequest): Serializer for NewsletterCampaign model.
        body (NewsletterCampaignRequest): Serializer for NewsletterCampaign model.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        NewsletterCampaign
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
        NewsletterCampaignRequest,
        NewsletterCampaignRequest,
        NewsletterCampaignRequest,
    ],
) -> Response[NewsletterCampaign]:
    """Update Campaign

     Update a newsletter campaign.

    Args:
        id (int):
        body (NewsletterCampaignRequest): Serializer for NewsletterCampaign model.
        body (NewsletterCampaignRequest): Serializer for NewsletterCampaign model.
        body (NewsletterCampaignRequest): Serializer for NewsletterCampaign model.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[NewsletterCampaign]
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
        NewsletterCampaignRequest,
        NewsletterCampaignRequest,
        NewsletterCampaignRequest,
    ],
) -> Optional[NewsletterCampaign]:
    """Update Campaign

     Update a newsletter campaign.

    Args:
        id (int):
        body (NewsletterCampaignRequest): Serializer for NewsletterCampaign model.
        body (NewsletterCampaignRequest): Serializer for NewsletterCampaign model.
        body (NewsletterCampaignRequest): Serializer for NewsletterCampaign model.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        NewsletterCampaign
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
