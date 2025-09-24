from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.api_key import APIKey
from ...models.api_key_request import APIKeyRequest
from typing import cast
from uuid import UUID


def _get_kwargs(
    user_id: int,
    id: UUID,
    *,
    body: Union[
        APIKeyRequest,
        APIKeyRequest,
        APIKeyRequest,
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/api/payments/users/{user_id}/api-keys/{id}/".format(
            user_id=user_id,
            id=id,
        ),
    }

    if isinstance(body, APIKeyRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, APIKeyRequest):
        _kwargs["data"] = body.to_dict()

        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if isinstance(body, APIKeyRequest):
        _kwargs["files"] = body.to_multipart()

        headers["Content-Type"] = "multipart/form-data"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[APIKey]:
    if response.status_code == 200:
        response_200 = APIKey.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[APIKey]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    user_id: int,
    id: UUID,
    *,
    client: AuthenticatedClient,
    body: Union[
        APIKeyRequest,
        APIKeyRequest,
        APIKeyRequest,
    ],
) -> Response[APIKey]:
    """Nested ViewSet for user API keys: /users/{user_id}/api-keys/

    Args:
        user_id (int): API key owner
        id (UUID): Unique identifier
        body (APIKeyRequest): API key with usage stats.
        body (APIKeyRequest): API key with usage stats.
        body (APIKeyRequest): API key with usage stats.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIKey]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        id=id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    user_id: int,
    id: UUID,
    *,
    client: AuthenticatedClient,
    body: Union[
        APIKeyRequest,
        APIKeyRequest,
        APIKeyRequest,
    ],
) -> Optional[APIKey]:
    """Nested ViewSet for user API keys: /users/{user_id}/api-keys/

    Args:
        user_id (int): API key owner
        id (UUID): Unique identifier
        body (APIKeyRequest): API key with usage stats.
        body (APIKeyRequest): API key with usage stats.
        body (APIKeyRequest): API key with usage stats.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIKey
    """

    return sync_detailed(
        user_id=user_id,
        id=id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    user_id: int,
    id: UUID,
    *,
    client: AuthenticatedClient,
    body: Union[
        APIKeyRequest,
        APIKeyRequest,
        APIKeyRequest,
    ],
) -> Response[APIKey]:
    """Nested ViewSet for user API keys: /users/{user_id}/api-keys/

    Args:
        user_id (int): API key owner
        id (UUID): Unique identifier
        body (APIKeyRequest): API key with usage stats.
        body (APIKeyRequest): API key with usage stats.
        body (APIKeyRequest): API key with usage stats.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIKey]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        id=id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    user_id: int,
    id: UUID,
    *,
    client: AuthenticatedClient,
    body: Union[
        APIKeyRequest,
        APIKeyRequest,
        APIKeyRequest,
    ],
) -> Optional[APIKey]:
    """Nested ViewSet for user API keys: /users/{user_id}/api-keys/

    Args:
        user_id (int): API key owner
        id (UUID): Unique identifier
        body (APIKeyRequest): API key with usage stats.
        body (APIKeyRequest): API key with usage stats.
        body (APIKeyRequest): API key with usage stats.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIKey
    """

    return (
        await asyncio_detailed(
            user_id=user_id,
            id=id,
            client=client,
            body=body,
        )
    ).parsed
