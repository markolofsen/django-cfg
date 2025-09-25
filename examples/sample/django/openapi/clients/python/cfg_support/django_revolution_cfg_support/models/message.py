from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime

if TYPE_CHECKING:
    from ..models.sender import Sender


T = TypeVar("T", bound="Message")


@_attrs_define
class Message:
    """
    Attributes:
        uuid (UUID):
        ticket (UUID):
        sender (Sender):
        is_from_author (bool): Check if this message is from the ticket author.
        text (str):
        created_at (datetime.datetime):
    """

    uuid: UUID
    ticket: UUID
    sender: "Sender"
    is_from_author: bool
    text: str
    created_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.sender import Sender

        uuid = str(self.uuid)

        ticket = str(self.ticket)

        sender = self.sender.to_dict()

        is_from_author = self.is_from_author

        text = self.text

        created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "uuid": uuid,
                "ticket": ticket,
                "sender": sender,
                "is_from_author": is_from_author,
                "text": text,
                "created_at": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.sender import Sender

        d = dict(src_dict)
        uuid = UUID(d.pop("uuid"))

        ticket = UUID(d.pop("ticket"))

        sender = Sender.from_dict(d.pop("sender"))

        is_from_author = d.pop("is_from_author")

        text = d.pop("text")

        created_at = isoparse(d.pop("created_at"))

        message = cls(
            uuid=uuid,
            ticket=ticket,
            sender=sender,
            is_from_author=is_from_author,
            text=text,
            created_at=created_at,
        )

        message.additional_properties = d
        return message

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
