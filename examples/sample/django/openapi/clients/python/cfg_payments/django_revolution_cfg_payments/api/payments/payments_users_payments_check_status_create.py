from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.universal_payment import UniversalPayment
from ...models.universal_payment_request import UniversalPaymentRequest
from typing import cast
from uuid import UUID


def _get_kwargs(
    user_id: int,
    id: UUID,
    *,
    body: Union[
        UniversalPaymentRequest,
        UniversalPaymentRequest,
        UniversalPaymentRequest,
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/payments/users/{user_id}/payments/{id}/check_status/".format(
            user_id=user_id,
            id=id,
        ),
    }

    if isinstance(body, UniversalPaymentRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, UniversalPaymentRequest):
        _kwargs["data"] = body.to_dict()

        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if isinstance(body, UniversalPaymentRequest):
        _kwargs["files"] = body.to_multipart()

        headers["Content-Type"] = "multipart/form-data"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[UniversalPayment]:
    if response.status_code == 200:
        response_200 = UniversalPayment.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[UniversalPayment]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    user_id: int,
    id: UUID,
    *,
    client: AuthenticatedClient,
    body: Union[
        UniversalPaymentRequest,
        UniversalPaymentRequest,
        UniversalPaymentRequest,
    ],
) -> Response[UniversalPayment]:
    """Check payment status via provider API.

    Args:
        user_id (int): User who initiated this payment
        id (UUID): Unique identifier
        body (UniversalPaymentRequest): Universal payment with status info.
        body (UniversalPaymentRequest): Universal payment with status info.
        body (UniversalPaymentRequest): Universal payment with status info.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UniversalPayment]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        id=id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    user_id: int,
    id: UUID,
    *,
    client: AuthenticatedClient,
    body: Union[
        UniversalPaymentRequest,
        UniversalPaymentRequest,
        UniversalPaymentRequest,
    ],
) -> Optional[UniversalPayment]:
    """Check payment status via provider API.

    Args:
        user_id (int): User who initiated this payment
        id (UUID): Unique identifier
        body (UniversalPaymentRequest): Universal payment with status info.
        body (UniversalPaymentRequest): Universal payment with status info.
        body (UniversalPaymentRequest): Universal payment with status info.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UniversalPayment
    """

    return sync_detailed(
        user_id=user_id,
        id=id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    user_id: int,
    id: UUID,
    *,
    client: AuthenticatedClient,
    body: Union[
        UniversalPaymentRequest,
        UniversalPaymentRequest,
        UniversalPaymentRequest,
    ],
) -> Response[UniversalPayment]:
    """Check payment status via provider API.

    Args:
        user_id (int): User who initiated this payment
        id (UUID): Unique identifier
        body (UniversalPaymentRequest): Universal payment with status info.
        body (UniversalPaymentRequest): Universal payment with status info.
        body (UniversalPaymentRequest): Universal payment with status info.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UniversalPayment]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        id=id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    user_id: int,
    id: UUID,
    *,
    client: AuthenticatedClient,
    body: Union[
        UniversalPaymentRequest,
        UniversalPaymentRequest,
        UniversalPaymentRequest,
    ],
) -> Optional[UniversalPayment]:
    """Check payment status via provider API.

    Args:
        user_id (int): User who initiated this payment
        id (UUID): Unique identifier
        body (UniversalPaymentRequest): Universal payment with status info.
        body (UniversalPaymentRequest): Universal payment with status info.
        body (UniversalPaymentRequest): Universal payment with status info.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UniversalPayment
    """

    return (
        await asyncio_detailed(
            user_id=user_id,
            id=id,
            client=client,
            body=body,
        )
    ).parsed
