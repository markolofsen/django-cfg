from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.paginated_currency_list_list import PaginatedCurrencyListList
from ...models.payments_currencies_list_currency_type import check_payments_currencies_list_currency_type
from ...models.payments_currencies_list_currency_type import PaymentsCurrenciesListCurrencyType
from ...types import UNSET, Unset
from typing import cast
from typing import Union


def _get_kwargs(
    *,
    currency_type: Union[Unset, PaymentsCurrenciesListCurrencyType] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_currency_type: Union[Unset, str] = UNSET
    if not isinstance(currency_type, Unset):
        json_currency_type = currency_type

    params["currency_type"] = json_currency_type

    params["is_active"] = is_active

    params["page"] = page

    params["page_size"] = page_size

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/payments/currencies/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[PaginatedCurrencyListList]:
    if response.status_code == 200:
        response_200 = PaginatedCurrencyListList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[PaginatedCurrencyListList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    currency_type: Union[Unset, PaymentsCurrenciesListCurrencyType] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
) -> Response[PaginatedCurrencyListList]:
    """Currency ViewSet: /currencies/

    Args:
        currency_type (Union[Unset, PaymentsCurrenciesListCurrencyType]):
        is_active (Union[Unset, bool]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedCurrencyListList]
    """

    kwargs = _get_kwargs(
        currency_type=currency_type,
        is_active=is_active,
        page=page,
        page_size=page_size,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    currency_type: Union[Unset, PaymentsCurrenciesListCurrencyType] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
) -> Optional[PaginatedCurrencyListList]:
    """Currency ViewSet: /currencies/

    Args:
        currency_type (Union[Unset, PaymentsCurrenciesListCurrencyType]):
        is_active (Union[Unset, bool]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedCurrencyListList
    """

    return sync_detailed(
        client=client,
        currency_type=currency_type,
        is_active=is_active,
        page=page,
        page_size=page_size,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    currency_type: Union[Unset, PaymentsCurrenciesListCurrencyType] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
) -> Response[PaginatedCurrencyListList]:
    """Currency ViewSet: /currencies/

    Args:
        currency_type (Union[Unset, PaymentsCurrenciesListCurrencyType]):
        is_active (Union[Unset, bool]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedCurrencyListList]
    """

    kwargs = _get_kwargs(
        currency_type=currency_type,
        is_active=is_active,
        page=page,
        page_size=page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    currency_type: Union[Unset, PaymentsCurrenciesListCurrencyType] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
) -> Optional[PaginatedCurrencyListList]:
    """Currency ViewSet: /currencies/

    Args:
        currency_type (Union[Unset, PaymentsCurrenciesListCurrencyType]):
        is_active (Union[Unset, bool]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedCurrencyListList
    """

    return (
        await asyncio_detailed(
            client=client,
            currency_type=currency_type,
            is_active=is_active,
            page=page,
            page_size=page_size,
        )
    ).parsed
