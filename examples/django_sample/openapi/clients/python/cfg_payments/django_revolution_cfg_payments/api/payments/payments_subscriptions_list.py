from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.paginated_subscription_list_list import PaginatedSubscriptionListList
from ...models.payments_subscriptions_list_status import check_payments_subscriptions_list_status
from ...models.payments_subscriptions_list_status import PaymentsSubscriptionsListStatus
from ...models.payments_subscriptions_list_tier import check_payments_subscriptions_list_tier
from ...models.payments_subscriptions_list_tier import PaymentsSubscriptionsListTier
from ...types import UNSET, Unset
from typing import cast
from typing import Union


def _get_kwargs(
    *,
    endpoint_group: Union[Unset, int] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    status: Union[Unset, PaymentsSubscriptionsListStatus] = UNSET,
    tier: Union[Unset, PaymentsSubscriptionsListTier] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["endpoint_group"] = endpoint_group

    params["page"] = page

    params["page_size"] = page_size

    json_status: Union[Unset, str] = UNSET
    if not isinstance(status, Unset):
        json_status = status

    params["status"] = json_status

    json_tier: Union[Unset, str] = UNSET
    if not isinstance(tier, Unset):
        json_tier = tier

    params["tier"] = json_tier

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/payments/subscriptions/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[PaginatedSubscriptionListList]:
    if response.status_code == 200:
        response_200 = PaginatedSubscriptionListList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[PaginatedSubscriptionListList]:
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
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    status: Union[Unset, PaymentsSubscriptionsListStatus] = UNSET,
    tier: Union[Unset, PaymentsSubscriptionsListTier] = UNSET,
) -> Response[PaginatedSubscriptionListList]:
    """Global subscription ViewSet: /subscriptions/

    Args:
        endpoint_group (Union[Unset, int]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        status (Union[Unset, PaymentsSubscriptionsListStatus]):
        tier (Union[Unset, PaymentsSubscriptionsListTier]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedSubscriptionListList]
    """

    kwargs = _get_kwargs(
        endpoint_group=endpoint_group,
        page=page,
        page_size=page_size,
        status=status,
        tier=tier,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    endpoint_group: Union[Unset, int] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    status: Union[Unset, PaymentsSubscriptionsListStatus] = UNSET,
    tier: Union[Unset, PaymentsSubscriptionsListTier] = UNSET,
) -> Optional[PaginatedSubscriptionListList]:
    """Global subscription ViewSet: /subscriptions/

    Args:
        endpoint_group (Union[Unset, int]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        status (Union[Unset, PaymentsSubscriptionsListStatus]):
        tier (Union[Unset, PaymentsSubscriptionsListTier]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedSubscriptionListList
    """

    return sync_detailed(
        client=client,
        endpoint_group=endpoint_group,
        page=page,
        page_size=page_size,
        status=status,
        tier=tier,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    endpoint_group: Union[Unset, int] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    status: Union[Unset, PaymentsSubscriptionsListStatus] = UNSET,
    tier: Union[Unset, PaymentsSubscriptionsListTier] = UNSET,
) -> Response[PaginatedSubscriptionListList]:
    """Global subscription ViewSet: /subscriptions/

    Args:
        endpoint_group (Union[Unset, int]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        status (Union[Unset, PaymentsSubscriptionsListStatus]):
        tier (Union[Unset, PaymentsSubscriptionsListTier]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedSubscriptionListList]
    """

    kwargs = _get_kwargs(
        endpoint_group=endpoint_group,
        page=page,
        page_size=page_size,
        status=status,
        tier=tier,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    endpoint_group: Union[Unset, int] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    status: Union[Unset, PaymentsSubscriptionsListStatus] = UNSET,
    tier: Union[Unset, PaymentsSubscriptionsListTier] = UNSET,
) -> Optional[PaginatedSubscriptionListList]:
    """Global subscription ViewSet: /subscriptions/

    Args:
        endpoint_group (Union[Unset, int]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        status (Union[Unset, PaymentsSubscriptionsListStatus]):
        tier (Union[Unset, PaymentsSubscriptionsListTier]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedSubscriptionListList
    """

    return (
        await asyncio_detailed(
            client=client,
            endpoint_group=endpoint_group,
            page=page,
            page_size=page_size,
            status=status,
            tier=tier,
        )
    ).parsed
