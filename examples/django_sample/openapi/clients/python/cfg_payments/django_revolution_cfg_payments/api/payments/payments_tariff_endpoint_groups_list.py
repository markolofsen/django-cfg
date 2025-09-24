from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.paginated_tariff_endpoint_group_list import PaginatedTariffEndpointGroupList
from ...types import UNSET, Unset
from typing import cast
from typing import Union


def _get_kwargs(
    *,
    endpoint_group: Union[Unset, int] = UNSET,
    is_enabled: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    tariff: Union[Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["endpoint_group"] = endpoint_group

    params["is_enabled"] = is_enabled

    params["page"] = page

    params["page_size"] = page_size

    params["tariff"] = tariff

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/payments/tariff-endpoint-groups/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[PaginatedTariffEndpointGroupList]:
    if response.status_code == 200:
        response_200 = PaginatedTariffEndpointGroupList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[PaginatedTariffEndpointGroupList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    endpoint_group: Union[Unset, int] = UNSET,
    is_enabled: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    tariff: Union[Unset, int] = UNSET,
) -> Response[PaginatedTariffEndpointGroupList]:
    """Tariff Endpoint Group ViewSet: /tariff-endpoint-groups/

    Args:
        endpoint_group (Union[Unset, int]):
        is_enabled (Union[Unset, bool]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        tariff (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedTariffEndpointGroupList]
    """

    kwargs = _get_kwargs(
        endpoint_group=endpoint_group,
        is_enabled=is_enabled,
        page=page,
        page_size=page_size,
        tariff=tariff,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    endpoint_group: Union[Unset, int] = UNSET,
    is_enabled: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    tariff: Union[Unset, int] = UNSET,
) -> Optional[PaginatedTariffEndpointGroupList]:
    """Tariff Endpoint Group ViewSet: /tariff-endpoint-groups/

    Args:
        endpoint_group (Union[Unset, int]):
        is_enabled (Union[Unset, bool]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        tariff (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedTariffEndpointGroupList
    """

    return sync_detailed(
        client=client,
        endpoint_group=endpoint_group,
        is_enabled=is_enabled,
        page=page,
        page_size=page_size,
        tariff=tariff,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    endpoint_group: Union[Unset, int] = UNSET,
    is_enabled: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    tariff: Union[Unset, int] = UNSET,
) -> Response[PaginatedTariffEndpointGroupList]:
    """Tariff Endpoint Group ViewSet: /tariff-endpoint-groups/

    Args:
        endpoint_group (Union[Unset, int]):
        is_enabled (Union[Unset, bool]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        tariff (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedTariffEndpointGroupList]
    """

    kwargs = _get_kwargs(
        endpoint_group=endpoint_group,
        is_enabled=is_enabled,
        page=page,
        page_size=page_size,
        tariff=tariff,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    endpoint_group: Union[Unset, int] = UNSET,
    is_enabled: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    tariff: Union[Unset, int] = UNSET,
) -> Optional[PaginatedTariffEndpointGroupList]:
    """Tariff Endpoint Group ViewSet: /tariff-endpoint-groups/

    Args:
        endpoint_group (Union[Unset, int]):
        is_enabled (Union[Unset, bool]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        tariff (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedTariffEndpointGroupList
    """

    return (
        await asyncio_detailed(
            client=client,
            endpoint_group=endpoint_group,
            is_enabled=is_enabled,
            page=page,
            page_size=page_size,
            tariff=tariff,
        )
    ).parsed
