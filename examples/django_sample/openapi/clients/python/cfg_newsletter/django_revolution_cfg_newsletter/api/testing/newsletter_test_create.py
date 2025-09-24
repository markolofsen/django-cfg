from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.newsletter_test_create_response_200 import NewsletterTestCreateResponse200
from ...models.newsletter_test_create_response_400 import NewsletterTestCreateResponse400
from ...models.test_email_request import TestEmailRequest
from typing import cast


def _get_kwargs(
    *,
    body: Union[
        TestEmailRequest,
        TestEmailRequest,
        TestEmailRequest,
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/newsletter/test/",
    }

    if isinstance(body, TestEmailRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, TestEmailRequest):
        _kwargs["data"] = body.to_dict()

        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if isinstance(body, TestEmailRequest):
        _kwargs["files"] = body.to_multipart()

        headers["Content-Type"] = "multipart/form-data"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[NewsletterTestCreateResponse200, NewsletterTestCreateResponse400]]:
    if response.status_code == 200:
        response_200 = NewsletterTestCreateResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = NewsletterTestCreateResponse400.from_dict(response.json())

        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[NewsletterTestCreateResponse200, NewsletterTestCreateResponse400]]:
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
        TestEmailRequest,
        TestEmailRequest,
        TestEmailRequest,
    ],
) -> Response[Union[NewsletterTestCreateResponse200, NewsletterTestCreateResponse400]]:
    """Test Email Sending

     Send a test email to verify mailer configuration.

    Args:
        body (TestEmailRequest): Simple serializer for test email.
        body (TestEmailRequest): Simple serializer for test email.
        body (TestEmailRequest): Simple serializer for test email.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[NewsletterTestCreateResponse200, NewsletterTestCreateResponse400]]
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
        TestEmailRequest,
        TestEmailRequest,
        TestEmailRequest,
    ],
) -> Optional[Union[NewsletterTestCreateResponse200, NewsletterTestCreateResponse400]]:
    """Test Email Sending

     Send a test email to verify mailer configuration.

    Args:
        body (TestEmailRequest): Simple serializer for test email.
        body (TestEmailRequest): Simple serializer for test email.
        body (TestEmailRequest): Simple serializer for test email.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[NewsletterTestCreateResponse200, NewsletterTestCreateResponse400]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: Union[
        TestEmailRequest,
        TestEmailRequest,
        TestEmailRequest,
    ],
) -> Response[Union[NewsletterTestCreateResponse200, NewsletterTestCreateResponse400]]:
    """Test Email Sending

     Send a test email to verify mailer configuration.

    Args:
        body (TestEmailRequest): Simple serializer for test email.
        body (TestEmailRequest): Simple serializer for test email.
        body (TestEmailRequest): Simple serializer for test email.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[NewsletterTestCreateResponse200, NewsletterTestCreateResponse400]]
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
        TestEmailRequest,
        TestEmailRequest,
        TestEmailRequest,
    ],
) -> Optional[Union[NewsletterTestCreateResponse200, NewsletterTestCreateResponse400]]:
    """Test Email Sending

     Send a test email to verify mailer configuration.

    Args:
        body (TestEmailRequest): Simple serializer for test email.
        body (TestEmailRequest): Simple serializer for test email.
        body (TestEmailRequest): Simple serializer for test email.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[NewsletterTestCreateResponse200, NewsletterTestCreateResponse400]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
