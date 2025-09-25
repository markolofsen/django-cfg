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


T = TypeVar("T", bound="Category")


@_attrs_define
class Category:
    """Serializer for blog categories.

    Attributes:
        id (int):
        name (str):
        slug (str):
        posts_count (int):
        children (str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        description (Union[Unset, str]):
        color (Union[Unset, str]): Hex color code
        meta_title (Union[Unset, str]):
        meta_description (Union[Unset, str]):
        parent (Union[None, Unset, int]):
    """

    id: int
    name: str
    slug: str
    posts_count: int
    children: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    description: Union[Unset, str] = UNSET
    color: Union[Unset, str] = UNSET
    meta_title: Union[Unset, str] = UNSET
    meta_description: Union[Unset, str] = UNSET
    parent: Union[None, Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        slug = self.slug

        posts_count = self.posts_count

        children = self.children

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        description = self.description

        color = self.color

        meta_title = self.meta_title

        meta_description = self.meta_description

        parent: Union[None, Unset, int]
        if isinstance(self.parent, Unset):
            parent = UNSET
        else:
            parent = self.parent

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "slug": slug,
                "posts_count": posts_count,
                "children": children,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if color is not UNSET:
            field_dict["color"] = color
        if meta_title is not UNSET:
            field_dict["meta_title"] = meta_title
        if meta_description is not UNSET:
            field_dict["meta_description"] = meta_description
        if parent is not UNSET:
            field_dict["parent"] = parent

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        slug = d.pop("slug")

        posts_count = d.pop("posts_count")

        children = d.pop("children")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        description = d.pop("description", UNSET)

        color = d.pop("color", UNSET)

        meta_title = d.pop("meta_title", UNSET)

        meta_description = d.pop("meta_description", UNSET)

        def _parse_parent(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        parent = _parse_parent(d.pop("parent", UNSET))

        category = cls(
            id=id,
            name=name,
            slug=slug,
            posts_count=posts_count,
            children=children,
            created_at=created_at,
            updated_at=updated_at,
            description=description,
            color=color,
            meta_title=meta_title,
            meta_description=meta_description,
            parent=parent,
        )

        category.additional_properties = d
        return category

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
