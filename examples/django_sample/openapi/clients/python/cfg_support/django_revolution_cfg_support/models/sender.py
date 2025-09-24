from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast, Union


T = TypeVar("T", bound="Sender")


@_attrs_define
class Sender:
    """
    Attributes:
        id (int):
        display_username (str): Get formatted username for display.
        email (str):
        avatar (Union[None, str]):
        initials (str): Get user's initials for avatar fallback.
        is_staff (bool): Designates whether the user can log into this admin site.
        is_superuser (bool): Designates that this user has all permissions without explicitly assigning them.
    """

    id: int
    display_username: str
    email: str
    avatar: Union[None, str]
    initials: str
    is_staff: bool
    is_superuser: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        display_username = self.display_username

        email = self.email

        avatar: Union[None, str]
        avatar = self.avatar

        initials = self.initials

        is_staff = self.is_staff

        is_superuser = self.is_superuser

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "display_username": display_username,
                "email": email,
                "avatar": avatar,
                "initials": initials,
                "is_staff": is_staff,
                "is_superuser": is_superuser,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        display_username = d.pop("display_username")

        email = d.pop("email")

        def _parse_avatar(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        avatar = _parse_avatar(d.pop("avatar"))

        initials = d.pop("initials")

        is_staff = d.pop("is_staff")

        is_superuser = d.pop("is_superuser")

        sender = cls(
            id=id,
            display_username=display_username,
            email=email,
            avatar=avatar,
            initials=initials,
            is_staff=is_staff,
            is_superuser=is_superuser,
        )

        sender.additional_properties = d
        return sender

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
