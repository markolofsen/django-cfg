from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import File, FileTypes
from ..types import UNSET, Unset
from io import BytesIO
from typing import cast, Union
from typing import Union


T = TypeVar("T", bound="AuthorRequest")


@_attrs_define
class AuthorRequest:
    """Serializer for post authors.

    Attributes:
        username (str): Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.
        first_name (Union[Unset, str]):
        last_name (Union[Unset, str]):
        avatar (Union[File, None, Unset]):
    """

    username: str
    first_name: Union[Unset, str] = UNSET
    last_name: Union[Unset, str] = UNSET
    avatar: Union[File, None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        username = self.username

        first_name = self.first_name

        last_name = self.last_name

        avatar: Union[FileTypes, None, Unset]
        if isinstance(self.avatar, Unset):
            avatar = UNSET
        elif isinstance(self.avatar, File):
            avatar = self.avatar.to_tuple()

        else:
            avatar = self.avatar

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "username": username,
            }
        )
        if first_name is not UNSET:
            field_dict["first_name"] = first_name
        if last_name is not UNSET:
            field_dict["last_name"] = last_name
        if avatar is not UNSET:
            field_dict["avatar"] = avatar

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        username = d.pop("username")

        first_name = d.pop("first_name", UNSET)

        last_name = d.pop("last_name", UNSET)

        def _parse_avatar(data: object) -> Union[File, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, bytes):
                    raise TypeError()
                avatar_type_0 = File(payload=BytesIO(data))

                return avatar_type_0
            except:  # noqa: E722
                pass
            return cast(Union[File, None, Unset], data)

        avatar = _parse_avatar(d.pop("avatar", UNSET))

        author_request = cls(
            username=username,
            first_name=first_name,
            last_name=last_name,
            avatar=avatar,
        )

        author_request.additional_properties = d
        return author_request

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
