from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.post_list_status import check_post_list_status
from ..models.post_list_status import PostListStatus
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
import datetime

if TYPE_CHECKING:
    from ..models.tag import Tag
    from ..models.category import Category
    from ..models.author import Author


T = TypeVar("T", bound="PostList")


@_attrs_define
class PostList:
    """Serializer for post list view.

    Attributes:
        id (int):
        title (str):
        author (Author): Serializer for post authors.
        category (Category): Serializer for blog categories.
        tags (list['Tag']):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        slug (Union[Unset, str]):
        excerpt (Union[Unset, str]): Brief description
        status (Union[Unset, PostListStatus]): * `draft` - Draft
            * `published` - Published
            * `archived` - Archived
        is_featured (Union[Unset, bool]):
        featured_image (Union[None, Unset, str]):
        featured_image_alt (Union[Unset, str]):
        views_count (Union[Unset, int]):
        likes_count (Union[Unset, int]):
        comments_count (Union[Unset, int]):
        shares_count (Union[Unset, int]):
        published_at (Union[None, Unset, datetime.datetime]):
    """

    id: int
    title: str
    author: "Author"
    category: "Category"
    tags: list["Tag"]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    slug: Union[Unset, str] = UNSET
    excerpt: Union[Unset, str] = UNSET
    status: Union[Unset, PostListStatus] = UNSET
    is_featured: Union[Unset, bool] = UNSET
    featured_image: Union[None, Unset, str] = UNSET
    featured_image_alt: Union[Unset, str] = UNSET
    views_count: Union[Unset, int] = UNSET
    likes_count: Union[Unset, int] = UNSET
    comments_count: Union[Unset, int] = UNSET
    shares_count: Union[Unset, int] = UNSET
    published_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.tag import Tag
        from ..models.category import Category
        from ..models.author import Author

        id = self.id

        title = self.title

        author = self.author.to_dict()

        category = self.category.to_dict()

        tags = []
        for tags_item_data in self.tags:
            tags_item = tags_item_data.to_dict()
            tags.append(tags_item)

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        slug = self.slug

        excerpt = self.excerpt

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status

        is_featured = self.is_featured

        featured_image: Union[None, Unset, str]
        if isinstance(self.featured_image, Unset):
            featured_image = UNSET
        else:
            featured_image = self.featured_image

        featured_image_alt = self.featured_image_alt

        views_count = self.views_count

        likes_count = self.likes_count

        comments_count = self.comments_count

        shares_count = self.shares_count

        published_at: Union[None, Unset, str]
        if isinstance(self.published_at, Unset):
            published_at = UNSET
        elif isinstance(self.published_at, datetime.datetime):
            published_at = self.published_at.isoformat()
        else:
            published_at = self.published_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "title": title,
                "author": author,
                "category": category,
                "tags": tags,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if slug is not UNSET:
            field_dict["slug"] = slug
        if excerpt is not UNSET:
            field_dict["excerpt"] = excerpt
        if status is not UNSET:
            field_dict["status"] = status
        if is_featured is not UNSET:
            field_dict["is_featured"] = is_featured
        if featured_image is not UNSET:
            field_dict["featured_image"] = featured_image
        if featured_image_alt is not UNSET:
            field_dict["featured_image_alt"] = featured_image_alt
        if views_count is not UNSET:
            field_dict["views_count"] = views_count
        if likes_count is not UNSET:
            field_dict["likes_count"] = likes_count
        if comments_count is not UNSET:
            field_dict["comments_count"] = comments_count
        if shares_count is not UNSET:
            field_dict["shares_count"] = shares_count
        if published_at is not UNSET:
            field_dict["published_at"] = published_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tag import Tag
        from ..models.category import Category
        from ..models.author import Author

        d = dict(src_dict)
        id = d.pop("id")

        title = d.pop("title")

        author = Author.from_dict(d.pop("author"))

        category = Category.from_dict(d.pop("category"))

        tags = []
        _tags = d.pop("tags")
        for tags_item_data in _tags:
            tags_item = Tag.from_dict(tags_item_data)

            tags.append(tags_item)

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        slug = d.pop("slug", UNSET)

        excerpt = d.pop("excerpt", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, PostListStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = check_post_list_status(_status)

        is_featured = d.pop("is_featured", UNSET)

        def _parse_featured_image(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        featured_image = _parse_featured_image(d.pop("featured_image", UNSET))

        featured_image_alt = d.pop("featured_image_alt", UNSET)

        views_count = d.pop("views_count", UNSET)

        likes_count = d.pop("likes_count", UNSET)

        comments_count = d.pop("comments_count", UNSET)

        shares_count = d.pop("shares_count", UNSET)

        def _parse_published_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                published_at_type_0 = isoparse(data)

                return published_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        published_at = _parse_published_at(d.pop("published_at", UNSET))

        post_list = cls(
            id=id,
            title=title,
            author=author,
            category=category,
            tags=tags,
            created_at=created_at,
            updated_at=updated_at,
            slug=slug,
            excerpt=excerpt,
            status=status,
            is_featured=is_featured,
            featured_image=featured_image,
            featured_image_alt=featured_image_alt,
            views_count=views_count,
            likes_count=likes_count,
            comments_count=comments_count,
            shares_count=shares_count,
            published_at=published_at,
        )

        post_list.additional_properties = d
        return post_list

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
