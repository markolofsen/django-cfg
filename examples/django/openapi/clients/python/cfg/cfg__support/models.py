from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..enums import PatchedTicketRequest.status, Ticket.status, TicketRequest.status


class TicketRequest(BaseModel):
    """
Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    user: int = ...
    subject: str = Field(min_length=1, max_length=255)
    status: TicketRequest.status = Field(None, description='* `open` - Open\n* `waiting_for_user` - Waiting for User\n* `waiting_for_admin` - Waiting for Admin\n* `resolved` - Resolved\n* `closed` - Closed')



class Ticket(BaseModel):
    """
Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    uuid: str = ...
    user: int = ...
    subject: str = Field(max_length=255)
    status: Ticket.status = Field(None, description='* `open` - Open\n* `waiting_for_user` - Waiting for User\n* `waiting_for_admin` - Waiting for Admin\n* `resolved` - Resolved\n* `closed` - Closed')
    created_at: str = ...
    unanswered_messages_count: int = Field(description='Get count of unanswered messages for this specific ticket.')



class MessageCreateRequest(BaseModel):
    """
Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    text: str = Field(min_length=1)



class MessageCreate(BaseModel):
    """
Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    text: str = ...



class Message(BaseModel):
    """
Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    uuid: str = ...
    ticket: str = ...
    sender: dict[str, Any] = ...
    is_from_author: bool = Field(description='Check if this message is from the ticket author.')
    text: str = ...
    created_at: str = ...



class MessageRequest(BaseModel):
    """
Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    text: str = Field(min_length=1)



class PatchedMessageRequest(BaseModel):
    """
Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    text: str = Field(None, min_length=1)



class PatchedTicketRequest(BaseModel):
    """
Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    user: int = None
    subject: str = Field(None, min_length=1, max_length=255)
    status: PatchedTicketRequest.status = Field(None, description='* `open` - Open\n* `waiting_for_user` - Waiting for User\n* `waiting_for_admin` - Waiting for Admin\n* `resolved` - Resolved\n* `closed` - Closed')



