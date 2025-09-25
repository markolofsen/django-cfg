from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.api_key_create import APIKeyCreate
from ...models.api_key_create_request import APIKeyCreateRequest
from typing import cast


def _get_kwargs(
    user_id: int,
    *,
    body: Union[
        APIKeyCreateRequest,
        APIKeyCreateRequest,
        APIKeyCreateRequest,
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/payments/users/{user_id}/api-keys/".format(
            user_id=user_id,
        ),
    }

    if isinstance(body, APIKeyCreateRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, APIKeyCreateRequest):
        _kwargs["data"] = body.to_dict()

        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if isinstance(body, APIKeyCreateRequest):
        _kwargs["files"] = body.to_multipart()

        headers["Content-Type"] = "multipart/form-data"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[APIKeyCreate]:
    if response.status_code == 201:
        response_201 = APIKeyCreate.from_dict(response.json())

        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[APIKeyCreate]:
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
    body: Union[
        APIKeyCreateRequest,
        APIKeyCreateRequest,
        APIKeyCreateRequest,
    ],
) -> Response[APIKeyCreate]:
    """Nested ViewSet for user API keys: /users/{user_id}/api-keys/

    Args:
        user_id (int): API key owner
        body (APIKeyCreateRequest): Create API key.
        body (APIKeyCreateRequest): Create API key.
        body (APIKeyCreateRequest): Create API key.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIKeyCreate]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    user_id: int,
    *,
    client: AuthenticatedClient,
    body: Union[
        APIKeyCreateRequest,
        APIKeyCreateRequest,
        APIKeyCreateRequest,
    ],
) -> Optional[APIKeyCreate]:
    """Nested ViewSet for user API keys: /users/{user_id}/api-keys/

    Args:
        user_id (int): API key owner
        body (APIKeyCreateRequest): Create API key.
        body (APIKeyCreateRequest): Create API key.
        body (APIKeyCreateRequest): Create API key.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIKeyCreate
    """

    return sync_detailed(
        user_id=user_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    user_id: int,
    *,
    client: AuthenticatedClient,
    body: Union[
        APIKeyCreateRequest,
        APIKeyCreateRequest,
        APIKeyCreateRequest,
    ],
) -> Response[APIKeyCreate]:
    """Nested ViewSet for user API keys: /users/{user_id}/api-keys/

    Args:
        user_id (int): API key owner
        body (APIKeyCreateRequest): Create API key.
        body (APIKeyCreateRequest): Create API key.
        body (APIKeyCreateRequest): Create API key.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[APIKeyCreate]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    user_id: int,
    *,
    client: AuthenticatedClient,
    body: Union[
        APIKeyCreateRequest,
        APIKeyCreateRequest,
        APIKeyCreateRequest,
    ],
) -> Optional[APIKeyCreate]:
    """Nested ViewSet for user API keys: /users/{user_id}/api-keys/

    Args:
        user_id (int): API key owner
        body (APIKeyCreateRequest): Create API key.
        body (APIKeyCreateRequest): Create API key.
        body (APIKeyCreateRequest): Create API key.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        APIKeyCreate
    """

    return (
        await asyncio_detailed(
            user_id=user_id,
            client=client,
            body=body,
        )
    ).parsed
