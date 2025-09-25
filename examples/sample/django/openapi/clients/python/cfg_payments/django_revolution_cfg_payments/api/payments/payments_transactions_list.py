from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.paginated_transaction_list_list import PaginatedTransactionListList
from ...models.payments_transactions_list_transaction_type import check_payments_transactions_list_transaction_type
from ...models.payments_transactions_list_transaction_type import PaymentsTransactionsListTransactionType
from ...types import UNSET, Unset
from typing import cast
from typing import Union
from uuid import UUID


def _get_kwargs(
    *,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    payment: Union[Unset, UUID] = UNSET,
    subscription: Union[Unset, UUID] = UNSET,
    transaction_type: Union[Unset, PaymentsTransactionsListTransactionType] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["page_size"] = page_size

    json_payment: Union[Unset, str] = UNSET
    if not isinstance(payment, Unset):
        json_payment = str(payment)
    params["payment"] = json_payment

    json_subscription: Union[Unset, str] = UNSET
    if not isinstance(subscription, Unset):
        json_subscription = str(subscription)
    params["subscription"] = json_subscription

    json_transaction_type: Union[Unset, str] = UNSET
    if not isinstance(transaction_type, Unset):
        json_transaction_type = transaction_type

    params["transaction_type"] = json_transaction_type

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/payments/transactions/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[PaginatedTransactionListList]:
    if response.status_code == 200:
        response_200 = PaginatedTransactionListList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[PaginatedTransactionListList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    payment: Union[Unset, UUID] = UNSET,
    subscription: Union[Unset, UUID] = UNSET,
    transaction_type: Union[Unset, PaymentsTransactionsListTransactionType] = UNSET,
) -> Response[PaginatedTransactionListList]:
    """Transaction ViewSet - read only.

    Args:
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        payment (Union[Unset, UUID]):
        subscription (Union[Unset, UUID]):
        transaction_type (Union[Unset, PaymentsTransactionsListTransactionType]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedTransactionListList]
    """

    kwargs = _get_kwargs(
        page=page,
        page_size=page_size,
        payment=payment,
        subscription=subscription,
        transaction_type=transaction_type,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    payment: Union[Unset, UUID] = UNSET,
    subscription: Union[Unset, UUID] = UNSET,
    transaction_type: Union[Unset, PaymentsTransactionsListTransactionType] = UNSET,
) -> Optional[PaginatedTransactionListList]:
    """Transaction ViewSet - read only.

    Args:
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        payment (Union[Unset, UUID]):
        subscription (Union[Unset, UUID]):
        transaction_type (Union[Unset, PaymentsTransactionsListTransactionType]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedTransactionListList
    """

    return sync_detailed(
        client=client,
        page=page,
        page_size=page_size,
        payment=payment,
        subscription=subscription,
        transaction_type=transaction_type,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    payment: Union[Unset, UUID] = UNSET,
    subscription: Union[Unset, UUID] = UNSET,
    transaction_type: Union[Unset, PaymentsTransactionsListTransactionType] = UNSET,
) -> Response[PaginatedTransactionListList]:
    """Transaction ViewSet - read only.

    Args:
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        payment (Union[Unset, UUID]):
        subscription (Union[Unset, UUID]):
        transaction_type (Union[Unset, PaymentsTransactionsListTransactionType]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedTransactionListList]
    """

    kwargs = _get_kwargs(
        page=page,
        page_size=page_size,
        payment=payment,
        subscription=subscription,
        transaction_type=transaction_type,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    payment: Union[Unset, UUID] = UNSET,
    subscription: Union[Unset, UUID] = UNSET,
    transaction_type: Union[Unset, PaymentsTransactionsListTransactionType] = UNSET,
) -> Optional[PaginatedTransactionListList]:
    """Transaction ViewSet - read only.

    Args:
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        payment (Union[Unset, UUID]):
        subscription (Union[Unset, UUID]):
        transaction_type (Union[Unset, PaymentsTransactionsListTransactionType]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedTransactionListList
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            page_size=page_size,
            payment=payment,
            subscription=subscription,
            transaction_type=transaction_type,
        )
    ).parsed
