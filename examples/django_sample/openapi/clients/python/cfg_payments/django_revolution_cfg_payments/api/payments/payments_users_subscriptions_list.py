from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.paginated_subscription_list_list import PaginatedSubscriptionListList
from ...models.payments_users_subscriptions_list_status import check_payments_users_subscriptions_list_status
from ...models.payments_users_subscriptions_list_status import PaymentsUsersSubscriptionsListStatus
from ...models.payments_users_subscriptions_list_tier import check_payments_users_subscriptions_list_tier
from ...models.payments_users_subscriptions_list_tier import PaymentsUsersSubscriptionsListTier
from ...types import UNSET, Unset
from typing import cast
from typing import Union


def _get_kwargs(
    user_id: int,
    *,
    endpoint_group: Union[Unset, int] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    status: Union[Unset, PaymentsUsersSubscriptionsListStatus] = UNSET,
    tier: Union[Unset, PaymentsUsersSubscriptionsListTier] = UNSET,
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
        "url": "/api/payments/users/{user_id}/subscriptions/".format(
            user_id=user_id,
        ),
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
    user_id: int,
    *,
    client: AuthenticatedClient,
    endpoint_group: Union[Unset, int] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    status: Union[Unset, PaymentsUsersSubscriptionsListStatus] = UNSET,
    tier: Union[Unset, PaymentsUsersSubscriptionsListTier] = UNSET,
) -> Response[PaginatedSubscriptionListList]:
    """Nested ViewSet for user subscriptions: /users/{user_id}/subscriptions/

    Args:
        user_id (int): Subscriber
        endpoint_group (Union[Unset, int]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        status (Union[Unset, PaymentsUsersSubscriptionsListStatus]):
        tier (Union[Unset, PaymentsUsersSubscriptionsListTier]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedSubscriptionListList]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
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
    user_id: int,
    *,
    client: AuthenticatedClient,
    endpoint_group: Union[Unset, int] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    status: Union[Unset, PaymentsUsersSubscriptionsListStatus] = UNSET,
    tier: Union[Unset, PaymentsUsersSubscriptionsListTier] = UNSET,
) -> Optional[PaginatedSubscriptionListList]:
    """Nested ViewSet for user subscriptions: /users/{user_id}/subscriptions/

    Args:
        user_id (int): Subscriber
        endpoint_group (Union[Unset, int]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        status (Union[Unset, PaymentsUsersSubscriptionsListStatus]):
        tier (Union[Unset, PaymentsUsersSubscriptionsListTier]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedSubscriptionListList
    """

    return sync_detailed(
        user_id=user_id,
        client=client,
        endpoint_group=endpoint_group,
        page=page,
        page_size=page_size,
        status=status,
        tier=tier,
    ).parsed


async def asyncio_detailed(
    user_id: int,
    *,
    client: AuthenticatedClient,
    endpoint_group: Union[Unset, int] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    status: Union[Unset, PaymentsUsersSubscriptionsListStatus] = UNSET,
    tier: Union[Unset, PaymentsUsersSubscriptionsListTier] = UNSET,
) -> Response[PaginatedSubscriptionListList]:
    """Nested ViewSet for user subscriptions: /users/{user_id}/subscriptions/

    Args:
        user_id (int): Subscriber
        endpoint_group (Union[Unset, int]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        status (Union[Unset, PaymentsUsersSubscriptionsListStatus]):
        tier (Union[Unset, PaymentsUsersSubscriptionsListTier]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedSubscriptionListList]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        endpoint_group=endpoint_group,
        page=page,
        page_size=page_size,
        status=status,
        tier=tier,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    user_id: int,
    *,
    client: AuthenticatedClient,
    endpoint_group: Union[Unset, int] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    status: Union[Unset, PaymentsUsersSubscriptionsListStatus] = UNSET,
    tier: Union[Unset, PaymentsUsersSubscriptionsListTier] = UNSET,
) -> Optional[PaginatedSubscriptionListList]:
    """Nested ViewSet for user subscriptions: /users/{user_id}/subscriptions/

    Args:
        user_id (int): Subscriber
        endpoint_group (Union[Unset, int]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        status (Union[Unset, PaymentsUsersSubscriptionsListStatus]):
        tier (Union[Unset, PaymentsUsersSubscriptionsListTier]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedSubscriptionListList
    """

    return (
        await asyncio_detailed(
            user_id=user_id,
            client=client,
            endpoint_group=endpoint_group,
            page=page,
            page_size=page_size,
            status=status,
            tier=tier,
        )
    ).parsed
