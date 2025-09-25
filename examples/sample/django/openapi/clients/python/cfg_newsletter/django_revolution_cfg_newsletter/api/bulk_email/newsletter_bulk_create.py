from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.bulk_email_request import BulkEmailRequest
from ...models.newsletter_bulk_create_response_200 import NewsletterBulkCreateResponse200
from ...models.newsletter_bulk_create_response_400 import NewsletterBulkCreateResponse400
from typing import cast


def _get_kwargs(
    *,
    body: Union[
        BulkEmailRequest,
        BulkEmailRequest,
        BulkEmailRequest,
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/newsletter/bulk/",
    }

    if isinstance(body, BulkEmailRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, BulkEmailRequest):
        _kwargs["data"] = body.to_dict()

        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if isinstance(body, BulkEmailRequest):
        _kwargs["files"] = body.to_multipart()

        headers["Content-Type"] = "multipart/form-data"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[NewsletterBulkCreateResponse200, NewsletterBulkCreateResponse400]]:
    if response.status_code == 200:
        response_200 = NewsletterBulkCreateResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = NewsletterBulkCreateResponse400.from_dict(response.json())

        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[NewsletterBulkCreateResponse200, NewsletterBulkCreateResponse400]]:
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
        BulkEmailRequest,
        BulkEmailRequest,
        BulkEmailRequest,
    ],
) -> Response[Union[NewsletterBulkCreateResponse200, NewsletterBulkCreateResponse400]]:
    """Send Bulk Email

     Send bulk emails to multiple recipients using base email template.

    Args:
        body (BulkEmailRequest): Simple serializer for bulk email.
        body (BulkEmailRequest): Simple serializer for bulk email.
        body (BulkEmailRequest): Simple serializer for bulk email.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[NewsletterBulkCreateResponse200, NewsletterBulkCreateResponse400]]
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
        BulkEmailRequest,
        BulkEmailRequest,
        BulkEmailRequest,
    ],
) -> Optional[Union[NewsletterBulkCreateResponse200, NewsletterBulkCreateResponse400]]:
    """Send Bulk Email

     Send bulk emails to multiple recipients using base email template.

    Args:
        body (BulkEmailRequest): Simple serializer for bulk email.
        body (BulkEmailRequest): Simple serializer for bulk email.
        body (BulkEmailRequest): Simple serializer for bulk email.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[NewsletterBulkCreateResponse200, NewsletterBulkCreateResponse400]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: Union[
        BulkEmailRequest,
        BulkEmailRequest,
        BulkEmailRequest,
    ],
) -> Response[Union[NewsletterBulkCreateResponse200, NewsletterBulkCreateResponse400]]:
    """Send Bulk Email

     Send bulk emails to multiple recipients using base email template.

    Args:
        body (BulkEmailRequest): Simple serializer for bulk email.
        body (BulkEmailRequest): Simple serializer for bulk email.
        body (BulkEmailRequest): Simple serializer for bulk email.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[NewsletterBulkCreateResponse200, NewsletterBulkCreateResponse400]]
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
        BulkEmailRequest,
        BulkEmailRequest,
        BulkEmailRequest,
    ],
) -> Optional[Union[NewsletterBulkCreateResponse200, NewsletterBulkCreateResponse400]]:
    """Send Bulk Email

     Send bulk emails to multiple recipients using base email template.

    Args:
        body (BulkEmailRequest): Simple serializer for bulk email.
        body (BulkEmailRequest): Simple serializer for bulk email.
        body (BulkEmailRequest): Simple serializer for bulk email.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[NewsletterBulkCreateResponse200, NewsletterBulkCreateResponse400]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
