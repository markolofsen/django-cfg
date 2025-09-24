from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.ticket_status import check_ticket_status
from ..models.ticket_status import TicketStatus
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import Union
from uuid import UUID
import datetime


T = TypeVar("T", bound="Ticket")


@_attrs_define
class Ticket:
    """
    Attributes:
        uuid (UUID):
        user (int):
        subject (str):
        created_at (datetime.datetime):
        unanswered_messages_count (int): Get count of unanswered messages for this specific ticket.
        status (Union[Unset, TicketStatus]): * `open` - Open
            * `waiting_for_user` - Waiting for User
            * `waiting_for_admin` - Waiting for Admin
            * `resolved` - Resolved
            * `closed` - Closed
    """

    uuid: UUID
    user: int
    subject: str
    created_at: datetime.datetime
    unanswered_messages_count: int
    status: Union[Unset, TicketStatus] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uuid = str(self.uuid)

        user = self.user

        subject = self.subject

        created_at = self.created_at.isoformat()

        unanswered_messages_count = self.unanswered_messages_count

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "uuid": uuid,
                "user": user,
                "subject": subject,
                "created_at": created_at,
                "unanswered_messages_count": unanswered_messages_count,
            }
        )
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        uuid = UUID(d.pop("uuid"))

        user = d.pop("user")

        subject = d.pop("subject")

        created_at = isoparse(d.pop("created_at"))

        unanswered_messages_count = d.pop("unanswered_messages_count")

        _status = d.pop("status", UNSET)
        status: Union[Unset, TicketStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = check_ticket_status(_status)

        ticket = cls(
            uuid=uuid,
            user=user,
            subject=subject,
            created_at=created_at,
            unanswered_messages_count=unanswered_messages_count,
            status=status,
        )

        ticket.additional_properties = d
        return ticket

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
