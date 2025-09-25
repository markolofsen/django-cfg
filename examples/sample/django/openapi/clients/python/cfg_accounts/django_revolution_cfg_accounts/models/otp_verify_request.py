from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field
import json
from .. import types

from ..types import UNSET, Unset

from ..models.otp_verify_request_channel import check_otp_verify_request_channel
from ..models.otp_verify_request_channel import OTPVerifyRequestChannel
from ..types import UNSET, Unset
from typing import cast
from typing import Union


T = TypeVar("T", bound="OTPVerifyRequest")


@_attrs_define
class OTPVerifyRequest:
    """Serializer for OTP verification.

    Attributes:
        identifier (str): Email address or phone number used for OTP request
        otp (str):
        channel (Union[Unset, OTPVerifyRequestChannel]): Delivery channel: 'email' or 'phone'. Auto-detected if not
            provided.

            * `email` - Email
            * `phone` - Phone
        source_url (Union[Unset, str]): Source URL for tracking login (e.g., https://dashboard.unrealon.com)
    """

    identifier: str
    otp: str
    channel: Union[Unset, OTPVerifyRequestChannel] = UNSET
    source_url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        identifier = self.identifier

        otp = self.otp

        channel: Union[Unset, str] = UNSET
        if not isinstance(self.channel, Unset):
            channel = self.channel

        source_url = self.source_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "identifier": identifier,
                "otp": otp,
            }
        )
        if channel is not UNSET:
            field_dict["channel"] = channel
        if source_url is not UNSET:
            field_dict["source_url"] = source_url

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        files.append(("identifier", (None, str(self.identifier).encode(), "text/plain")))

        files.append(("otp", (None, str(self.otp).encode(), "text/plain")))

        if not isinstance(self.channel, Unset):
            files.append(("channel", (None, str(self.channel).encode(), "text/plain")))

        if not isinstance(self.source_url, Unset):
            files.append(("source_url", (None, str(self.source_url).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        identifier = d.pop("identifier")

        otp = d.pop("otp")

        _channel = d.pop("channel", UNSET)
        channel: Union[Unset, OTPVerifyRequestChannel]
        if isinstance(_channel, Unset):
            channel = UNSET
        else:
            channel = check_otp_verify_request_channel(_channel)

        source_url = d.pop("source_url", UNSET)

        otp_verify_request = cls(
            identifier=identifier,
            otp=otp,
            channel=channel,
            source_url=source_url,
        )

        otp_verify_request.additional_properties = d
        return otp_verify_request

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
