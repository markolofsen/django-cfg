from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.paginated_order_list_list import PaginatedOrderListList
from ...models.shop_orders_list_status import check_shop_orders_list_status
from ...models.shop_orders_list_status import ShopOrdersListStatus
from ...types import UNSET, Unset
from typing import cast
from typing import Union


def _get_kwargs(
    *,
    customer: Union[Unset, int] = UNSET,
    ordering: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = UNSET,
    status: Union[Unset, ShopOrdersListStatus] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["customer"] = customer

    params["ordering"] = ordering

    params["page"] = page

    params["page_size"] = page_size

    params["search"] = search

    json_status: Union[Unset, str] = UNSET
    if not isinstance(status, Unset):
        json_status = status

    params["status"] = json_status

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/shop/orders/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[PaginatedOrderListList]:
    if response.status_code == 200:
        response_200 = PaginatedOrderListList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[PaginatedOrderListList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    customer: Union[Unset, int] = UNSET,
    ordering: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = UNSET,
    status: Union[Unset, ShopOrdersListStatus] = UNSET,
) -> Response[PaginatedOrderListList]:
    """List orders

     Get a list of orders (admin only)

    Args:
        customer (Union[Unset, int]):
        ordering (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        search (Union[Unset, str]):
        status (Union[Unset, ShopOrdersListStatus]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedOrderListList]
    """

    kwargs = _get_kwargs(
        customer=customer,
        ordering=ordering,
        page=page,
        page_size=page_size,
        search=search,
        status=status,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    customer: Union[Unset, int] = UNSET,
    ordering: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = UNSET,
    status: Union[Unset, ShopOrdersListStatus] = UNSET,
) -> Optional[PaginatedOrderListList]:
    """List orders

     Get a list of orders (admin only)

    Args:
        customer (Union[Unset, int]):
        ordering (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        search (Union[Unset, str]):
        status (Union[Unset, ShopOrdersListStatus]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedOrderListList
    """

    return sync_detailed(
        client=client,
        customer=customer,
        ordering=ordering,
        page=page,
        page_size=page_size,
        search=search,
        status=status,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    customer: Union[Unset, int] = UNSET,
    ordering: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = UNSET,
    status: Union[Unset, ShopOrdersListStatus] = UNSET,
) -> Response[PaginatedOrderListList]:
    """List orders

     Get a list of orders (admin only)

    Args:
        customer (Union[Unset, int]):
        ordering (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        search (Union[Unset, str]):
        status (Union[Unset, ShopOrdersListStatus]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedOrderListList]
    """

    kwargs = _get_kwargs(
        customer=customer,
        ordering=ordering,
        page=page,
        page_size=page_size,
        search=search,
        status=status,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    customer: Union[Unset, int] = UNSET,
    ordering: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = UNSET,
    status: Union[Unset, ShopOrdersListStatus] = UNSET,
) -> Optional[PaginatedOrderListList]:
    """List orders

     Get a list of orders (admin only)

    Args:
        customer (Union[Unset, int]):
        ordering (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        search (Union[Unset, str]):
        status (Union[Unset, ShopOrdersListStatus]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedOrderListList
    """

    return (
        await asyncio_detailed(
            client=client,
            customer=customer,
            ordering=ordering,
            page=page,
            page_size=page_size,
            search=search,
            status=status,
        )
    ).parsed
