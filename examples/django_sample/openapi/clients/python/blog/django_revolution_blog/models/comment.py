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

if TYPE_CHECKING:
    from ..models.author import Author


T = TypeVar("T", bound="Comment")


@_attrs_define
class Comment:
    """Serializer for blog comments.

    Attributes:
        id (int):
        content (str):
        author (Author): Serializer for post authors.
        is_approved (bool):
        likes_count (int):
        replies (str):
        can_edit (str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        parent (Union[None, Unset, int]):
    """

    id: int
    content: str
    author: "Author"
    is_approved: bool
    likes_count: int
    replies: str
    can_edit: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    parent: Union[None, Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.author import Author

        id = self.id

        content = self.content

        author = self.author.to_dict()

        is_approved = self.is_approved

        likes_count = self.likes_count

        replies = self.replies

        can_edit = self.can_edit

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

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
                "content": content,
                "author": author,
                "is_approved": is_approved,
                "likes_count": likes_count,
                "replies": replies,
                "can_edit": can_edit,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if parent is not UNSET:
            field_dict["parent"] = parent

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.author import Author

        d = dict(src_dict)
        id = d.pop("id")

        content = d.pop("content")

        author = Author.from_dict(d.pop("author"))

        is_approved = d.pop("is_approved")

        likes_count = d.pop("likes_count")

        replies = d.pop("replies")

        can_edit = d.pop("can_edit")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        def _parse_parent(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        parent = _parse_parent(d.pop("parent", UNSET))

        comment = cls(
            id=id,
            content=content,
            author=author,
            is_approved=is_approved,
            likes_count=likes_count,
            replies=replies,
            can_edit=can_edit,
            created_at=created_at,
            updated_at=updated_at,
            parent=parent,
        )

        comment.additional_properties = d
        return comment

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
