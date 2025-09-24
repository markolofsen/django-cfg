from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.message import Message
from ...models.message_request import MessageRequest
from typing import cast
from uuid import UUID


def _get_kwargs(
    ticket_uuid: UUID,
    uuid: UUID,
    *,
    body: Union[
        MessageRequest,
        MessageRequest,
        MessageRequest,
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/api/support/tickets/{ticket_uuid}/messages/{uuid}/".format(
            ticket_uuid=ticket_uuid,
            uuid=uuid,
        ),
    }

    if isinstance(body, MessageRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, MessageRequest):
        _kwargs["data"] = body.to_dict()

        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if isinstance(body, MessageRequest):
        _kwargs["files"] = body.to_multipart()

        headers["Content-Type"] = "multipart/form-data"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Message]:
    if response.status_code == 200:
        response_200 = Message.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Message]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    ticket_uuid: UUID,
    uuid: UUID,
    *,
    client: AuthenticatedClient,
    body: Union[
        MessageRequest,
        MessageRequest,
        MessageRequest,
    ],
) -> Response[Message]:
    """ViewSet for managing support messages.

    Args:
        ticket_uuid (UUID):
        uuid (UUID):
        body (MessageRequest):
        body (MessageRequest):
        body (MessageRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Message]
    """

    kwargs = _get_kwargs(
        ticket_uuid=ticket_uuid,
        uuid=uuid,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    ticket_uuid: UUID,
    uuid: UUID,
    *,
    client: AuthenticatedClient,
    body: Union[
        MessageRequest,
        MessageRequest,
        MessageRequest,
    ],
) -> Optional[Message]:
    """ViewSet for managing support messages.

    Args:
        ticket_uuid (UUID):
        uuid (UUID):
        body (MessageRequest):
        body (MessageRequest):
        body (MessageRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Message
    """

    return sync_detailed(
        ticket_uuid=ticket_uuid,
        uuid=uuid,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    ticket_uuid: UUID,
    uuid: UUID,
    *,
    client: AuthenticatedClient,
    body: Union[
        MessageRequest,
        MessageRequest,
        MessageRequest,
    ],
) -> Response[Message]:
    """ViewSet for managing support messages.

    Args:
        ticket_uuid (UUID):
        uuid (UUID):
        body (MessageRequest):
        body (MessageRequest):
        body (MessageRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Message]
    """

    kwargs = _get_kwargs(
        ticket_uuid=ticket_uuid,
        uuid=uuid,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    ticket_uuid: UUID,
    uuid: UUID,
    *,
    client: AuthenticatedClient,
    body: Union[
        MessageRequest,
        MessageRequest,
        MessageRequest,
    ],
) -> Optional[Message]:
    """ViewSet for managing support messages.

    Args:
        ticket_uuid (UUID):
        uuid (UUID):
        body (MessageRequest):
        body (MessageRequest):
        body (MessageRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Message
    """

    return (
        await asyncio_detailed(
            ticket_uuid=ticket_uuid,
            uuid=uuid,
            client=client,
            body=body,
        )
    ).parsed
