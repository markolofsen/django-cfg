from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.message_create import MessageCreate
from ...models.message_create_request import MessageCreateRequest
from typing import cast
from uuid import UUID


def _get_kwargs(
    ticket_uuid: UUID,
    *,
    body: Union[
        MessageCreateRequest,
        MessageCreateRequest,
        MessageCreateRequest,
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/support/tickets/{ticket_uuid}/messages/".format(
            ticket_uuid=ticket_uuid,
        ),
    }

    if isinstance(body, MessageCreateRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, MessageCreateRequest):
        _kwargs["data"] = body.to_dict()

        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if isinstance(body, MessageCreateRequest):
        _kwargs["files"] = body.to_multipart()

        headers["Content-Type"] = "multipart/form-data"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[MessageCreate]:
    if response.status_code == 201:
        response_201 = MessageCreate.from_dict(response.json())

        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[MessageCreate]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    ticket_uuid: UUID,
    *,
    client: AuthenticatedClient,
    body: Union[
        MessageCreateRequest,
        MessageCreateRequest,
        MessageCreateRequest,
    ],
) -> Response[MessageCreate]:
    """ViewSet for managing support messages.

    Args:
        ticket_uuid (UUID):
        body (MessageCreateRequest):
        body (MessageCreateRequest):
        body (MessageCreateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[MessageCreate]
    """

    kwargs = _get_kwargs(
        ticket_uuid=ticket_uuid,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    ticket_uuid: UUID,
    *,
    client: AuthenticatedClient,
    body: Union[
        MessageCreateRequest,
        MessageCreateRequest,
        MessageCreateRequest,
    ],
) -> Optional[MessageCreate]:
    """ViewSet for managing support messages.

    Args:
        ticket_uuid (UUID):
        body (MessageCreateRequest):
        body (MessageCreateRequest):
        body (MessageCreateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        MessageCreate
    """

    return sync_detailed(
        ticket_uuid=ticket_uuid,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    ticket_uuid: UUID,
    *,
    client: AuthenticatedClient,
    body: Union[
        MessageCreateRequest,
        MessageCreateRequest,
        MessageCreateRequest,
    ],
) -> Response[MessageCreate]:
    """ViewSet for managing support messages.

    Args:
        ticket_uuid (UUID):
        body (MessageCreateRequest):
        body (MessageCreateRequest):
        body (MessageCreateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[MessageCreate]
    """

    kwargs = _get_kwargs(
        ticket_uuid=ticket_uuid,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    ticket_uuid: UUID,
    *,
    client: AuthenticatedClient,
    body: Union[
        MessageCreateRequest,
        MessageCreateRequest,
        MessageCreateRequest,
    ],
) -> Optional[MessageCreate]:
    """ViewSet for managing support messages.

    Args:
        ticket_uuid (UUID):
        body (MessageCreateRequest):
        body (MessageCreateRequest):
        body (MessageCreateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        MessageCreate
    """

    return (
        await asyncio_detailed(
            ticket_uuid=ticket_uuid,
            client=client,
            body=body,
        )
    ).parsed
