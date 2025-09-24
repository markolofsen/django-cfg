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
    """Serializer for shop categories.

    Attributes:
        id (int):
        name (str):
        slug (str):
        products_count (int):
        children (str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        description (Union[Unset, str]):
        image (Union[None, Unset, str]):
        parent (Union[None, Unset, int]):
        meta_title (Union[Unset, str]):
        meta_description (Union[Unset, str]):
        is_active (Union[Unset, bool]):
        sort_order (Union[Unset, int]):
    """

    id: int
    name: str
    slug: str
    products_count: int
    children: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    description: Union[Unset, str] = UNSET
    image: Union[None, Unset, str] = UNSET
    parent: Union[None, Unset, int] = UNSET
    meta_title: Union[Unset, str] = UNSET
    meta_description: Union[Unset, str] = UNSET
    is_active: Union[Unset, bool] = UNSET
    sort_order: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        slug = self.slug

        products_count = self.products_count

        children = self.children

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        description = self.description

        image: Union[None, Unset, str]
        if isinstance(self.image, Unset):
            image = UNSET
        else:
            image = self.image

        parent: Union[None, Unset, int]
        if isinstance(self.parent, Unset):
            parent = UNSET
        else:
            parent = self.parent

        meta_title = self.meta_title

        meta_description = self.meta_description

        is_active = self.is_active

        sort_order = self.sort_order

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "slug": slug,
                "products_count": products_count,
                "children": children,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if image is not UNSET:
            field_dict["image"] = image
        if parent is not UNSET:
            field_dict["parent"] = parent
        if meta_title is not UNSET:
            field_dict["meta_title"] = meta_title
        if meta_description is not UNSET:
            field_dict["meta_description"] = meta_description
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if sort_order is not UNSET:
            field_dict["sort_order"] = sort_order

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        slug = d.pop("slug")

        products_count = d.pop("products_count")

        children = d.pop("children")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        description = d.pop("description", UNSET)

        def _parse_image(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        image = _parse_image(d.pop("image", UNSET))

        def _parse_parent(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        parent = _parse_parent(d.pop("parent", UNSET))

        meta_title = d.pop("meta_title", UNSET)

        meta_description = d.pop("meta_description", UNSET)

        is_active = d.pop("is_active", UNSET)

        sort_order = d.pop("sort_order", UNSET)

        category = cls(
            id=id,
            name=name,
            slug=slug,
            products_count=products_count,
            children=children,
            created_at=created_at,
            updated_at=updated_at,
            description=description,
            image=image,
            parent=parent,
            meta_title=meta_title,
            meta_description=meta_description,
            is_active=is_active,
            sort_order=sort_order,
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
