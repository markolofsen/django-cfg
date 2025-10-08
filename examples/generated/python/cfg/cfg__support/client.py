from __future__ import annotations

import httpx

from .models import *


class CfgSupportAPI:
    """API endpoints for Support."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def tickets_list(self) -> None:
        """
        ViewSet for managing support tickets.
        """
        url = "/django_cfg_support/tickets/"
        response = await self._client.get(url)
        response.raise_for_status()
        return None


    async def tickets_create(self, data: TicketRequest) -> Ticket:
        """
        ViewSet for managing support tickets.
        """
        url = "/django_cfg_support/tickets/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return Ticket.model_validate(response.json())


    async def tickets_messages_list(self, ticket_uuid: str) -> None:
        """
        ViewSet for managing support messages.
        """
        url = f"/django_cfg_support/tickets/{ticket_uuid}/messages/"
        response = await self._client.get(url)
        response.raise_for_status()
        return None


    async def tickets_messages_create(self, ticket_uuid: str, data: MessageCreateRequest) -> MessageCreate:
        """
        ViewSet for managing support messages.
        """
        url = f"/django_cfg_support/tickets/{ticket_uuid}/messages/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return MessageCreate.model_validate(response.json())


    async def tickets_messages_retrieve(self, ticket_uuid: str, uuid: str) -> Message:
        """
        ViewSet for managing support messages.
        """
        url = f"/django_cfg_support/tickets/{ticket_uuid}/messages/{uuid}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Message.model_validate(response.json())


    async def tickets_messages_update(self, ticket_uuid: str, uuid: str, data: MessageRequest) -> Message:
        """
        ViewSet for managing support messages.
        """
        url = f"/django_cfg_support/tickets/{ticket_uuid}/messages/{uuid}/"
        response = await self._client.put(url, json=data.model_dump())
        response.raise_for_status()
        return Message.model_validate(response.json())


    async def tickets_messages_partial_update(self, ticket_uuid: str, uuid: str, data: PatchedMessageRequest | None = None) -> Message:
        """
        ViewSet for managing support messages.
        """
        url = f"/django_cfg_support/tickets/{ticket_uuid}/messages/{uuid}/"
        response = await self._client.patch(url, json=data.model_dump() if data is not None else None)
        response.raise_for_status()
        return Message.model_validate(response.json())


    async def tickets_messages_destroy(self, ticket_uuid: str, uuid: str) -> None:
        """
        ViewSet for managing support messages.
        """
        url = f"/django_cfg_support/tickets/{ticket_uuid}/messages/{uuid}/"
        response = await self._client.delete(url)
        response.raise_for_status()
        return None


    async def tickets_retrieve(self, uuid: str) -> Ticket:
        """
        ViewSet for managing support tickets.
        """
        url = f"/django_cfg_support/tickets/{uuid}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Ticket.model_validate(response.json())


    async def tickets_update(self, uuid: str, data: TicketRequest) -> Ticket:
        """
        ViewSet for managing support tickets.
        """
        url = f"/django_cfg_support/tickets/{uuid}/"
        response = await self._client.put(url, json=data.model_dump())
        response.raise_for_status()
        return Ticket.model_validate(response.json())


    async def tickets_partial_update(self, uuid: str, data: PatchedTicketRequest | None = None) -> Ticket:
        """
        ViewSet for managing support tickets.
        """
        url = f"/django_cfg_support/tickets/{uuid}/"
        response = await self._client.patch(url, json=data.model_dump() if data is not None else None)
        response.raise_for_status()
        return Ticket.model_validate(response.json())


    async def tickets_destroy(self, uuid: str) -> None:
        """
        ViewSet for managing support tickets.
        """
        url = f"/django_cfg_support/tickets/{uuid}/"
        response = await self._client.delete(url)
        response.raise_for_status()
        return None


