from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.token_refresh import TokenRefresh
from ...models.token_refresh_request import TokenRefreshRequest
from typing import cast


def _get_kwargs(
    *,
    body: Union[
        TokenRefreshRequest,
        TokenRefreshRequest,
        TokenRefreshRequest,
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/accounts/token/refresh/",
    }

    if isinstance(body, TokenRefreshRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, TokenRefreshRequest):
        _kwargs["data"] = body.to_dict()

        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if isinstance(body, TokenRefreshRequest):
        _kwargs["files"] = body.to_multipart()

        headers["Content-Type"] = "multipart/form-data"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[TokenRefresh]:
    if response.status_code == 200:
        response_200 = TokenRefresh.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[TokenRefresh]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        TokenRefreshRequest,
        TokenRefreshRequest,
        TokenRefreshRequest,
    ],
) -> Response[TokenRefresh]:
    """Refresh JWT token.

    Args:
        body (TokenRefreshRequest):
        body (TokenRefreshRequest):
        body (TokenRefreshRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TokenRefresh]
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
    client: Union[AuthenticatedClient, Client],
    body: Union[
        TokenRefreshRequest,
        TokenRefreshRequest,
        TokenRefreshRequest,
    ],
) -> Optional[TokenRefresh]:
    """Refresh JWT token.

    Args:
        body (TokenRefreshRequest):
        body (TokenRefreshRequest):
        body (TokenRefreshRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TokenRefresh
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        TokenRefreshRequest,
        TokenRefreshRequest,
        TokenRefreshRequest,
    ],
) -> Response[TokenRefresh]:
    """Refresh JWT token.

    Args:
        body (TokenRefreshRequest):
        body (TokenRefreshRequest):
        body (TokenRefreshRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TokenRefresh]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        TokenRefreshRequest,
        TokenRefreshRequest,
        TokenRefreshRequest,
    ],
) -> Optional[TokenRefresh]:
    """Refresh JWT token.

    Args:
        body (TokenRefreshRequest):
        body (TokenRefreshRequest):
        body (TokenRefreshRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TokenRefresh
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
