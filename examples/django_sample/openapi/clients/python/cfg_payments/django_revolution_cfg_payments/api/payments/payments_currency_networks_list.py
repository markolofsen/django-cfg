from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.paginated_currency_network_list import PaginatedCurrencyNetworkList
from ...types import UNSET, Unset
from typing import cast
from typing import Union


def _get_kwargs(
    *,
    currency: Union[Unset, int] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    network_code: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["currency"] = currency

    params["is_active"] = is_active

    params["network_code"] = network_code

    params["page"] = page

    params["page_size"] = page_size

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/payments/currency-networks/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[PaginatedCurrencyNetworkList]:
    if response.status_code == 200:
        response_200 = PaginatedCurrencyNetworkList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[PaginatedCurrencyNetworkList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    currency: Union[Unset, int] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    network_code: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
) -> Response[PaginatedCurrencyNetworkList]:
    """Currency Network ViewSet: /currency-networks/

    Args:
        currency (Union[Unset, int]):
        is_active (Union[Unset, bool]):
        network_code (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedCurrencyNetworkList]
    """

    kwargs = _get_kwargs(
        currency=currency,
        is_active=is_active,
        network_code=network_code,
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
    currency: Union[Unset, int] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    network_code: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
) -> Optional[PaginatedCurrencyNetworkList]:
    """Currency Network ViewSet: /currency-networks/

    Args:
        currency (Union[Unset, int]):
        is_active (Union[Unset, bool]):
        network_code (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedCurrencyNetworkList
    """

    return sync_detailed(
        client=client,
        currency=currency,
        is_active=is_active,
        network_code=network_code,
        page=page,
        page_size=page_size,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    currency: Union[Unset, int] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    network_code: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
) -> Response[PaginatedCurrencyNetworkList]:
    """Currency Network ViewSet: /currency-networks/

    Args:
        currency (Union[Unset, int]):
        is_active (Union[Unset, bool]):
        network_code (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedCurrencyNetworkList]
    """

    kwargs = _get_kwargs(
        currency=currency,
        is_active=is_active,
        network_code=network_code,
        page=page,
        page_size=page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    currency: Union[Unset, int] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    network_code: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
) -> Optional[PaginatedCurrencyNetworkList]:
    """Currency Network ViewSet: /currency-networks/

    Args:
        currency (Union[Unset, int]):
        is_active (Union[Unset, bool]):
        network_code (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedCurrencyNetworkList
    """

    return (
        await asyncio_detailed(
            client=client,
            currency=currency,
            is_active=is_active,
            network_code=network_code,
            page=page,
            page_size=page_size,
        )
    ).parsed
