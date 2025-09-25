from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.patched_user_profile_update_request import PatchedUserProfileUpdateRequest
from ...models.user import User
from typing import cast


def _get_kwargs(
    *,
    body: Union[
        PatchedUserProfileUpdateRequest,
        PatchedUserProfileUpdateRequest,
        PatchedUserProfileUpdateRequest,
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/api/accounts/profile/update/",
    }

    if isinstance(body, PatchedUserProfileUpdateRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, PatchedUserProfileUpdateRequest):
        _kwargs["data"] = body.to_dict()

        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if isinstance(body, PatchedUserProfileUpdateRequest):
        _kwargs["files"] = body.to_multipart()

        headers["Content-Type"] = "multipart/form-data"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, User]]:
    if response.status_code == 200:
        response_200 = User.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = response.json()
        return response_400

    if response.status_code == 401:
        response_401 = response.json()
        return response_401

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, User]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: Union[
        PatchedUserProfileUpdateRequest,
        PatchedUserProfileUpdateRequest,
        PatchedUserProfileUpdateRequest,
    ],
) -> Response[Union[Any, User]]:
    """Update user profile

     Update the current authenticated user's profile information.

    Args:
        body (PatchedUserProfileUpdateRequest): Serializer for updating user profile.
        body (PatchedUserProfileUpdateRequest): Serializer for updating user profile.
        body (PatchedUserProfileUpdateRequest): Serializer for updating user profile.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, User]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: Union[
        PatchedUserProfileUpdateRequest,
        PatchedUserProfileUpdateRequest,
        PatchedUserProfileUpdateRequest,
    ],
) -> Optional[Union[Any, User]]:
    """Update user profile

     Update the current authenticated user's profile information.

    Args:
        body (PatchedUserProfileUpdateRequest): Serializer for updating user profile.
        body (PatchedUserProfileUpdateRequest): Serializer for updating user profile.
        body (PatchedUserProfileUpdateRequest): Serializer for updating user profile.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, User]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: Union[
        PatchedUserProfileUpdateRequest,
        PatchedUserProfileUpdateRequest,
        PatchedUserProfileUpdateRequest,
    ],
) -> Response[Union[Any, User]]:
    """Update user profile

     Update the current authenticated user's profile information.

    Args:
        body (PatchedUserProfileUpdateRequest): Serializer for updating user profile.
        body (PatchedUserProfileUpdateRequest): Serializer for updating user profile.
        body (PatchedUserProfileUpdateRequest): Serializer for updating user profile.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, User]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: Union[
        PatchedUserProfileUpdateRequest,
        PatchedUserProfileUpdateRequest,
        PatchedUserProfileUpdateRequest,
    ],
) -> Optional[Union[Any, User]]:
    """Update user profile

     Update the current authenticated user's profile information.

    Args:
        body (PatchedUserProfileUpdateRequest): Serializer for updating user profile.
        body (PatchedUserProfileUpdateRequest): Serializer for updating user profile.
        body (PatchedUserProfileUpdateRequest): Serializer for updating user profile.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, User]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
