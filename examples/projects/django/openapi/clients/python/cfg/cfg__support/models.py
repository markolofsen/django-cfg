from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..enums import PatchedTicketRequestStatus, TicketRequestStatus, TicketStatus


class PaginatedTicketList(BaseModel):
    """
    
    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    count: int = Field(description='Total number of items across all pages')
    page: int = Field(description='Current page number (1-based)')
    pages: int = Field(description='Total number of pages')
    page_size: int = Field(description='Number of items per page')
    has_next: bool = Field(description='Whether there is a next page')
    has_previous: bool = Field(description='Whether there is a previous page')
    next_page: int | None = Field(None, description='Next page number (null if no next page)')
    previous_page: int | None = Field(None, description='Previous page number (null if no previous page)')
    results: list[Any] = Field(description='Array of items for current page')



class Ticket(BaseModel):
    """
    
    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    uuid: Any = ...
    user: int = ...
    subject: str = Field(max_length=255)
    status: TicketStatus = Field(None, description='* `open` - Open\n* `waiting_for_user` - Waiting for User\n* `waiting_for_admin` - Waiting for Admin\n* `resolved` - Resolved\n* `closed` - Closed')
    created_at: Any = ...
    unanswered_messages_count: int = Field(description='Get count of unanswered messages for this specific ticket.')



class PaginatedMessageList(BaseModel):
    """
    
    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    count: int = Field(description='Total number of items across all pages')
    page: int = Field(description='Current page number (1-based)')
    pages: int = Field(description='Total number of pages')
    page_size: int = Field(description='Number of items per page')
    has_next: bool = Field(description='Whether there is a next page')
    has_previous: bool = Field(description='Whether there is a previous page')
    next_page: int | None = Field(None, description='Next page number (null if no next page)')
    previous_page: int | None = Field(None, description='Previous page number (null if no previous page)')
    results: list[Any] = Field(description='Array of items for current page')



class MessageCreate(BaseModel):
    """
    
    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    text: str = ...



class Message(BaseModel):
    """
    
    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    uuid: Any = ...
    ticket: Any = ...
    sender: Any = ...
    is_from_author: bool = Field(description='Check if this message is from the ticket author.')
    text: str = ...
    created_at: Any = ...



class TicketRequest(BaseModel):
    """
    
    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    user: int = ...
    subject: str = Field(min_length=1, max_length=255)
    status: TicketRequestStatus = Field(None, description='* `open` - Open\n* `waiting_for_user` - Waiting for User\n* `waiting_for_admin` - Waiting for Admin\n* `resolved` - Resolved\n* `closed` - Closed')



class MessageCreateRequest(BaseModel):
    """
    
    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    text: str = Field(min_length=1)



class MessageRequest(BaseModel):
    """
    
    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    text: str = Field(min_length=1)



class PatchedMessageRequest(BaseModel):
    """
    
    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    text: str = Field(None, min_length=1)



class PatchedTicketRequest(BaseModel):
    """
    
    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    user: int = None
    subject: str = Field(None, min_length=1, max_length=255)
    status: PatchedTicketRequestStatus = Field(None, description='* `open` - Open\n* `waiting_for_user` - Waiting for User\n* `waiting_for_admin` - Waiting for Admin\n* `resolved` - Resolved\n* `closed` - Closed')



