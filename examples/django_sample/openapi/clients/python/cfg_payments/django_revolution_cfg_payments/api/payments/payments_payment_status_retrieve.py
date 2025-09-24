from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.universal_payment import UniversalPayment
from typing import cast


def _get_kwargs(
    internal_payment_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/payments/payment/status/{internal_payment_id}/".format(
            internal_payment_id=internal_payment_id,
        ),
    }

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
    internal_payment_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[UniversalPayment]:
    """Generic view to check payment status.

    Args:
        internal_payment_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UniversalPayment]
    """

    kwargs = _get_kwargs(
        internal_payment_id=internal_payment_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    internal_payment_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[UniversalPayment]:
    """Generic view to check payment status.

    Args:
        internal_payment_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UniversalPayment
    """

    return sync_detailed(
        internal_payment_id=internal_payment_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    internal_payment_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[UniversalPayment]:
    """Generic view to check payment status.

    Args:
        internal_payment_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UniversalPayment]
    """

    kwargs = _get_kwargs(
        internal_payment_id=internal_payment_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    internal_payment_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[UniversalPayment]:
    """Generic view to check payment status.

    Args:
        internal_payment_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UniversalPayment
    """

    return (
        await asyncio_detailed(
            internal_payment_id=internal_payment_id,
            client=client,
        )
    ).parsed
