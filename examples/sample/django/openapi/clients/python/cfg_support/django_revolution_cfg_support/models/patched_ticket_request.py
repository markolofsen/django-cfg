from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field
import json
from .. import types

from ..types import UNSET, Unset

from ..models.patched_ticket_request_status import check_patched_ticket_request_status
from ..models.patched_ticket_request_status import PatchedTicketRequestStatus
from ..types import UNSET, Unset
from typing import cast
from typing import Union


T = TypeVar("T", bound="PatchedTicketRequest")


@_attrs_define
class PatchedTicketRequest:
    """
    Attributes:
        user (Union[Unset, int]):
        subject (Union[Unset, str]):
        status (Union[Unset, PatchedTicketRequestStatus]): * `open` - Open
            * `waiting_for_user` - Waiting for User
            * `waiting_for_admin` - Waiting for Admin
            * `resolved` - Resolved
            * `closed` - Closed
    """

    user: Union[Unset, int] = UNSET
    subject: Union[Unset, str] = UNSET
    status: Union[Unset, PatchedTicketRequestStatus] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user = self.user

        subject = self.subject

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if user is not UNSET:
            field_dict["user"] = user
        if subject is not UNSET:
            field_dict["subject"] = subject
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        if not isinstance(self.user, Unset):
            files.append(("user", (None, str(self.user).encode(), "text/plain")))

        if not isinstance(self.subject, Unset):
            files.append(("subject", (None, str(self.subject).encode(), "text/plain")))

        if not isinstance(self.status, Unset):
            files.append(("status", (None, str(self.status).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user = d.pop("user", UNSET)

        subject = d.pop("subject", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, PatchedTicketRequestStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = check_patched_ticket_request_status(_status)

        patched_ticket_request = cls(
            user=user,
            subject=subject,
            status=status,
        )

        patched_ticket_request.additional_properties = d
        return patched_ticket_request

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
