from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field
import json
from .. import types

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast, Union
from typing import Union


T = TypeVar("T", bound="PatchedCategoryRequest")


@_attrs_define
class PatchedCategoryRequest:
    """Serializer for blog categories.

    Attributes:
        name (Union[Unset, str]):
        description (Union[Unset, str]):
        color (Union[Unset, str]): Hex color code
        meta_title (Union[Unset, str]):
        meta_description (Union[Unset, str]):
        parent (Union[None, Unset, int]):
    """

    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    color: Union[Unset, str] = UNSET
    meta_title: Union[Unset, str] = UNSET
    meta_description: Union[Unset, str] = UNSET
    parent: Union[None, Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

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
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
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

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        if not isinstance(self.name, Unset):
            files.append(("name", (None, str(self.name).encode(), "text/plain")))

        if not isinstance(self.description, Unset):
            files.append(("description", (None, str(self.description).encode(), "text/plain")))

        if not isinstance(self.color, Unset):
            files.append(("color", (None, str(self.color).encode(), "text/plain")))

        if not isinstance(self.meta_title, Unset):
            files.append(("meta_title", (None, str(self.meta_title).encode(), "text/plain")))

        if not isinstance(self.meta_description, Unset):
            files.append(("meta_description", (None, str(self.meta_description).encode(), "text/plain")))

        if not isinstance(self.parent, Unset):
            if isinstance(self.parent, int):
                files.append(("parent", (None, str(self.parent).encode(), "text/plain")))
            else:
                files.append(("parent", (None, str(self.parent).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

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

        patched_category_request = cls(
            name=name,
            description=description,
            color=color,
            meta_title=meta_title,
            meta_description=meta_description,
            parent=parent,
        )

        patched_category_request.additional_properties = d
        return patched_category_request

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
