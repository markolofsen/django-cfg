from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field
import json
from .. import types

from ..types import UNSET, Unset

from ..models.post_detail_request_status import check_post_detail_request_status
from ..models.post_detail_request_status import PostDetailRequestStatus
from ..types import File, FileTypes
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from io import BytesIO
from typing import cast
from typing import cast, Union
from typing import Union
import datetime


T = TypeVar("T", bound="PostDetailRequest")


@_attrs_define
class PostDetailRequest:
    """Serializer for post detail view.

    Attributes:
        title (str):
        content (str):
        slug (Union[Unset, str]):
        excerpt (Union[Unset, str]): Brief description
        status (Union[Unset, PostDetailRequestStatus]): * `draft` - Draft
            * `published` - Published
            * `archived` - Archived
        is_featured (Union[Unset, bool]):
        allow_comments (Union[Unset, bool]):
        meta_title (Union[Unset, str]):
        meta_description (Union[Unset, str]):
        meta_keywords (Union[Unset, str]):
        featured_image (Union[File, None, Unset]):
        featured_image_alt (Union[Unset, str]):
        views_count (Union[Unset, int]):
        likes_count (Union[Unset, int]):
        comments_count (Union[Unset, int]):
        shares_count (Union[Unset, int]):
        published_at (Union[None, Unset, datetime.datetime]):
    """

    title: str
    content: str
    slug: Union[Unset, str] = UNSET
    excerpt: Union[Unset, str] = UNSET
    status: Union[Unset, PostDetailRequestStatus] = UNSET
    is_featured: Union[Unset, bool] = UNSET
    allow_comments: Union[Unset, bool] = UNSET
    meta_title: Union[Unset, str] = UNSET
    meta_description: Union[Unset, str] = UNSET
    meta_keywords: Union[Unset, str] = UNSET
    featured_image: Union[File, None, Unset] = UNSET
    featured_image_alt: Union[Unset, str] = UNSET
    views_count: Union[Unset, int] = UNSET
    likes_count: Union[Unset, int] = UNSET
    comments_count: Union[Unset, int] = UNSET
    shares_count: Union[Unset, int] = UNSET
    published_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        content = self.content

        slug = self.slug

        excerpt = self.excerpt

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status

        is_featured = self.is_featured

        allow_comments = self.allow_comments

        meta_title = self.meta_title

        meta_description = self.meta_description

        meta_keywords = self.meta_keywords

        featured_image: Union[FileTypes, None, Unset]
        if isinstance(self.featured_image, Unset):
            featured_image = UNSET
        elif isinstance(self.featured_image, File):
            featured_image = self.featured_image.to_tuple()

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
                "title": title,
                "content": content,
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
        if allow_comments is not UNSET:
            field_dict["allow_comments"] = allow_comments
        if meta_title is not UNSET:
            field_dict["meta_title"] = meta_title
        if meta_description is not UNSET:
            field_dict["meta_description"] = meta_description
        if meta_keywords is not UNSET:
            field_dict["meta_keywords"] = meta_keywords
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

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        files.append(("title", (None, str(self.title).encode(), "text/plain")))

        files.append(("content", (None, str(self.content).encode(), "text/plain")))

        if not isinstance(self.slug, Unset):
            files.append(("slug", (None, str(self.slug).encode(), "text/plain")))

        if not isinstance(self.excerpt, Unset):
            files.append(("excerpt", (None, str(self.excerpt).encode(), "text/plain")))

        if not isinstance(self.status, Unset):
            files.append(("status", (None, str(self.status).encode(), "text/plain")))

        if not isinstance(self.is_featured, Unset):
            files.append(("is_featured", (None, str(self.is_featured).encode(), "text/plain")))

        if not isinstance(self.allow_comments, Unset):
            files.append(("allow_comments", (None, str(self.allow_comments).encode(), "text/plain")))

        if not isinstance(self.meta_title, Unset):
            files.append(("meta_title", (None, str(self.meta_title).encode(), "text/plain")))

        if not isinstance(self.meta_description, Unset):
            files.append(("meta_description", (None, str(self.meta_description).encode(), "text/plain")))

        if not isinstance(self.meta_keywords, Unset):
            files.append(("meta_keywords", (None, str(self.meta_keywords).encode(), "text/plain")))

        if not isinstance(self.featured_image, Unset):
            if isinstance(self.featured_image, File):
                files.append(("featured_image", self.featured_image.to_tuple()))
            else:
                files.append(("featured_image", (None, str(self.featured_image).encode(), "text/plain")))

        if not isinstance(self.featured_image_alt, Unset):
            files.append(("featured_image_alt", (None, str(self.featured_image_alt).encode(), "text/plain")))

        if not isinstance(self.views_count, Unset):
            files.append(("views_count", (None, str(self.views_count).encode(), "text/plain")))

        if not isinstance(self.likes_count, Unset):
            files.append(("likes_count", (None, str(self.likes_count).encode(), "text/plain")))

        if not isinstance(self.comments_count, Unset):
            files.append(("comments_count", (None, str(self.comments_count).encode(), "text/plain")))

        if not isinstance(self.shares_count, Unset):
            files.append(("shares_count", (None, str(self.shares_count).encode(), "text/plain")))

        if not isinstance(self.published_at, Unset):
            if isinstance(self.published_at, datetime.datetime):
                files.append(("published_at", (None, self.published_at.isoformat().encode(), "text/plain")))
            else:
                files.append(("published_at", (None, str(self.published_at).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        title = d.pop("title")

        content = d.pop("content")

        slug = d.pop("slug", UNSET)

        excerpt = d.pop("excerpt", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, PostDetailRequestStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = check_post_detail_request_status(_status)

        is_featured = d.pop("is_featured", UNSET)

        allow_comments = d.pop("allow_comments", UNSET)

        meta_title = d.pop("meta_title", UNSET)

        meta_description = d.pop("meta_description", UNSET)

        meta_keywords = d.pop("meta_keywords", UNSET)

        def _parse_featured_image(data: object) -> Union[File, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, bytes):
                    raise TypeError()
                featured_image_type_0 = File(payload=BytesIO(data))

                return featured_image_type_0
            except:  # noqa: E722
                pass
            return cast(Union[File, None, Unset], data)

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

        post_detail_request = cls(
            title=title,
            content=content,
            slug=slug,
            excerpt=excerpt,
            status=status,
            is_featured=is_featured,
            allow_comments=allow_comments,
            meta_title=meta_title,
            meta_description=meta_description,
            meta_keywords=meta_keywords,
            featured_image=featured_image,
            featured_image_alt=featured_image_alt,
            views_count=views_count,
            likes_count=likes_count,
            comments_count=comments_count,
            shares_count=shares_count,
            published_at=published_at,
        )

        post_detail_request.additional_properties = d
        return post_detail_request

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
