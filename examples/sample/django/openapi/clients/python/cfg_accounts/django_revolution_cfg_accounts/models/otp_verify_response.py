from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
    from ..models.user import User


T = TypeVar("T", bound="OTPVerifyResponse")


@_attrs_define
class OTPVerifyResponse:
    """OTP verification response.

    Attributes:
        refresh (str): JWT refresh token
        access (str): JWT access token
        user (User): Serializer for user details.
    """

    refresh: str
    access: str
    user: "User"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.user import User

        refresh = self.refresh

        access = self.access

        user = self.user.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "refresh": refresh,
                "access": access,
                "user": user,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user import User

        d = dict(src_dict)
        refresh = d.pop("refresh")

        access = d.pop("access")

        user = User.from_dict(d.pop("user"))

        otp_verify_response = cls(
            refresh=refresh,
            access=access,
            user=user,
        )

        otp_verify_response.additional_properties = d
        return otp_verify_response

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
