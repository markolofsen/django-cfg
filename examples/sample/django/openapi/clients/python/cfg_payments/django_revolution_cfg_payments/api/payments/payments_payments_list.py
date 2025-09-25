from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.paginated_payment_list_list import PaginatedPaymentListList
from ...models.payments_payments_list_provider import check_payments_payments_list_provider
from ...models.payments_payments_list_provider import PaymentsPaymentsListProvider
from ...models.payments_payments_list_status import check_payments_payments_list_status
from ...models.payments_payments_list_status import PaymentsPaymentsListStatus
from ...types import UNSET, Unset
from typing import cast
from typing import Union


def _get_kwargs(
    *,
    currency_code: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    provider: Union[Unset, PaymentsPaymentsListProvider] = UNSET,
    status: Union[Unset, PaymentsPaymentsListStatus] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["currency_code"] = currency_code

    params["page"] = page

    params["page_size"] = page_size

    json_provider: Union[Unset, str] = UNSET
    if not isinstance(provider, Unset):
        json_provider = provider

    params["provider"] = json_provider

    json_status: Union[Unset, str] = UNSET
    if not isinstance(status, Unset):
        json_status = status

    params["status"] = json_status

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/payments/payments/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[PaginatedPaymentListList]:
    if response.status_code == 200:
        response_200 = PaginatedPaymentListList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[PaginatedPaymentListList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    currency_code: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    provider: Union[Unset, PaymentsPaymentsListProvider] = UNSET,
    status: Union[Unset, PaymentsPaymentsListStatus] = UNSET,
) -> Response[PaginatedPaymentListList]:
    """Global payment ViewSet: /payments/

    Args:
        currency_code (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        provider (Union[Unset, PaymentsPaymentsListProvider]):
        status (Union[Unset, PaymentsPaymentsListStatus]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedPaymentListList]
    """

    kwargs = _get_kwargs(
        currency_code=currency_code,
        page=page,
        page_size=page_size,
        provider=provider,
        status=status,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    currency_code: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    provider: Union[Unset, PaymentsPaymentsListProvider] = UNSET,
    status: Union[Unset, PaymentsPaymentsListStatus] = UNSET,
) -> Optional[PaginatedPaymentListList]:
    """Global payment ViewSet: /payments/

    Args:
        currency_code (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        provider (Union[Unset, PaymentsPaymentsListProvider]):
        status (Union[Unset, PaymentsPaymentsListStatus]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedPaymentListList
    """

    return sync_detailed(
        client=client,
        currency_code=currency_code,
        page=page,
        page_size=page_size,
        provider=provider,
        status=status,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    currency_code: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    provider: Union[Unset, PaymentsPaymentsListProvider] = UNSET,
    status: Union[Unset, PaymentsPaymentsListStatus] = UNSET,
) -> Response[PaginatedPaymentListList]:
    """Global payment ViewSet: /payments/

    Args:
        currency_code (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        provider (Union[Unset, PaymentsPaymentsListProvider]):
        status (Union[Unset, PaymentsPaymentsListStatus]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedPaymentListList]
    """

    kwargs = _get_kwargs(
        currency_code=currency_code,
        page=page,
        page_size=page_size,
        provider=provider,
        status=status,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    currency_code: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    provider: Union[Unset, PaymentsPaymentsListProvider] = UNSET,
    status: Union[Unset, PaymentsPaymentsListStatus] = UNSET,
) -> Optional[PaginatedPaymentListList]:
    """Global payment ViewSet: /payments/

    Args:
        currency_code (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        provider (Union[Unset, PaymentsPaymentsListProvider]):
        status (Union[Unset, PaymentsPaymentsListStatus]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedPaymentListList
    """

    return (
        await asyncio_detailed(
            client=client,
            currency_code=currency_code,
            page=page,
            page_size=page_size,
            provider=provider,
            status=status,
        )
    ).parsed
