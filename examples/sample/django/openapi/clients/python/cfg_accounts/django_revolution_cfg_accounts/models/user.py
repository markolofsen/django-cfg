from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
import datetime


T = TypeVar("T", bound="User")


@_attrs_define
class User:
    """Serializer for user details.

    Attributes:
        id (int):
        email (str):
        full_name (str): Get user's full name.
        initials (str): Get user's initials for avatar fallback.
        display_username (str): Get formatted username for display.
        is_staff (bool): Designates whether the user can log into this admin site.
        is_superuser (bool): Designates that this user has all permissions without explicitly assigning them.
        date_joined (datetime.datetime):
        last_login (Union[None, datetime.datetime]):
        unanswered_messages_count (int): Get count of unanswered messages for the user.
        first_name (Union[Unset, str]):
        last_name (Union[Unset, str]):
        company (Union[Unset, str]):
        phone (Union[Unset, str]):
        position (Union[Unset, str]):
        avatar (Union[None, Unset, str]):
    """

    id: int
    email: str
    full_name: str
    initials: str
    display_username: str
    is_staff: bool
    is_superuser: bool
    date_joined: datetime.datetime
    last_login: Union[None, datetime.datetime]
    unanswered_messages_count: int
    first_name: Union[Unset, str] = UNSET
    last_name: Union[Unset, str] = UNSET
    company: Union[Unset, str] = UNSET
    phone: Union[Unset, str] = UNSET
    position: Union[Unset, str] = UNSET
    avatar: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        email = self.email

        full_name = self.full_name

        initials = self.initials

        display_username = self.display_username

        is_staff = self.is_staff

        is_superuser = self.is_superuser

        date_joined = self.date_joined.isoformat()

        last_login: Union[None, str]
        if isinstance(self.last_login, datetime.datetime):
            last_login = self.last_login.isoformat()
        else:
            last_login = self.last_login

        unanswered_messages_count = self.unanswered_messages_count

        first_name = self.first_name

        last_name = self.last_name

        company = self.company

        phone = self.phone

        position = self.position

        avatar: Union[None, Unset, str]
        if isinstance(self.avatar, Unset):
            avatar = UNSET
        else:
            avatar = self.avatar

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "email": email,
                "full_name": full_name,
                "initials": initials,
                "display_username": display_username,
                "is_staff": is_staff,
                "is_superuser": is_superuser,
                "date_joined": date_joined,
                "last_login": last_login,
                "unanswered_messages_count": unanswered_messages_count,
            }
        )
        if first_name is not UNSET:
            field_dict["first_name"] = first_name
        if last_name is not UNSET:
            field_dict["last_name"] = last_name
        if company is not UNSET:
            field_dict["company"] = company
        if phone is not UNSET:
            field_dict["phone"] = phone
        if position is not UNSET:
            field_dict["position"] = position
        if avatar is not UNSET:
            field_dict["avatar"] = avatar

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        email = d.pop("email")

        full_name = d.pop("full_name")

        initials = d.pop("initials")

        display_username = d.pop("display_username")

        is_staff = d.pop("is_staff")

        is_superuser = d.pop("is_superuser")

        date_joined = isoparse(d.pop("date_joined"))

        def _parse_last_login(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_login_type_0 = isoparse(data)

                return last_login_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        last_login = _parse_last_login(d.pop("last_login"))

        unanswered_messages_count = d.pop("unanswered_messages_count")

        first_name = d.pop("first_name", UNSET)

        last_name = d.pop("last_name", UNSET)

        company = d.pop("company", UNSET)

        phone = d.pop("phone", UNSET)

        position = d.pop("position", UNSET)

        def _parse_avatar(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        avatar = _parse_avatar(d.pop("avatar", UNSET))

        user = cls(
            id=id,
            email=email,
            full_name=full_name,
            initials=initials,
            display_username=display_username,
            is_staff=is_staff,
            is_superuser=is_superuser,
            date_joined=date_joined,
            last_login=last_login,
            unanswered_messages_count=unanswered_messages_count,
            first_name=first_name,
            last_name=last_name,
            company=company,
            phone=phone,
            position=position,
            avatar=avatar,
        )

        user.additional_properties = d
        return user

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
