from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import Union
import datetime


T = TypeVar("T", bound="Newsletter")


@_attrs_define
class Newsletter:
    """Serializer for Newsletter model.

    Attributes:
        id (int):
        title (str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        subscribers_count (str):
        description (Union[Unset, str]):
        is_active (Union[Unset, bool]):
        auto_subscribe (Union[Unset, bool]): Automatically subscribe new users to this newsletter
    """

    id: int
    title: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    subscribers_count: str
    description: Union[Unset, str] = UNSET
    is_active: Union[Unset, bool] = UNSET
    auto_subscribe: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        title = self.title

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        subscribers_count = self.subscribers_count

        description = self.description

        is_active = self.is_active

        auto_subscribe = self.auto_subscribe

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "title": title,
                "created_at": created_at,
                "updated_at": updated_at,
                "subscribers_count": subscribers_count,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if auto_subscribe is not UNSET:
            field_dict["auto_subscribe"] = auto_subscribe

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        title = d.pop("title")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        subscribers_count = d.pop("subscribers_count")

        description = d.pop("description", UNSET)

        is_active = d.pop("is_active", UNSET)

        auto_subscribe = d.pop("auto_subscribe", UNSET)

        newsletter = cls(
            id=id,
            title=title,
            created_at=created_at,
            updated_at=updated_at,
            subscribers_count=subscribers_count,
            description=description,
            is_active=is_active,
            auto_subscribe=auto_subscribe,
        )

        newsletter.additional_properties = d
        return newsletter

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
