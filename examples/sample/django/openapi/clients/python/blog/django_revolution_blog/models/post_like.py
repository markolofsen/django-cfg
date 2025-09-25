from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.post_like_reaction import check_post_like_reaction
from ..models.post_like_reaction import PostLikeReaction
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import Union
import datetime

if TYPE_CHECKING:
    from ..models.author import Author


T = TypeVar("T", bound="PostLike")


@_attrs_define
class PostLike:
    """Serializer for post likes.

    Attributes:
        id (int):
        user (Author): Serializer for post authors.
        created_at (datetime.datetime):
        reaction (Union[Unset, PostLikeReaction]): * `like` - 👍
            * `love` - ❤️
            * `laugh` - 😂
            * `wow` - 😮
            * `sad` - 😢
            * `angry` - 😠
    """

    id: int
    user: "Author"
    created_at: datetime.datetime
    reaction: Union[Unset, PostLikeReaction] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.author import Author

        id = self.id

        user = self.user.to_dict()

        created_at = self.created_at.isoformat()

        reaction: Union[Unset, str] = UNSET
        if not isinstance(self.reaction, Unset):
            reaction = self.reaction

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "user": user,
                "created_at": created_at,
            }
        )
        if reaction is not UNSET:
            field_dict["reaction"] = reaction

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.author import Author

        d = dict(src_dict)
        id = d.pop("id")

        user = Author.from_dict(d.pop("user"))

        created_at = isoparse(d.pop("created_at"))

        _reaction = d.pop("reaction", UNSET)
        reaction: Union[Unset, PostLikeReaction]
        if isinstance(_reaction, Unset):
            reaction = UNSET
        else:
            reaction = check_post_like_reaction(_reaction)

        post_like = cls(
            id=id,
            user=user,
            created_at=created_at,
            reaction=reaction,
        )

        post_like.additional_properties = d
        return post_like

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
