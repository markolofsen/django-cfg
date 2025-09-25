from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field
import json
from .. import types

from ..types import UNSET, Unset

from ..models.post_create_request_status import check_post_create_request_status
from ..models.post_create_request_status import PostCreateRequestStatus
from ..types import File, FileTypes
from ..types import UNSET, Unset
from io import BytesIO
from typing import cast
from typing import cast, Union
from typing import Union


T = TypeVar("T", bound="PostCreateRequest")


@_attrs_define
class PostCreateRequest:
    """Serializer for post creation.

    Attributes:
        title (str):
        content (str):
        excerpt (Union[Unset, str]): Brief description
        category (Union[None, Unset, int]):
        tags (Union[Unset, list[int]]):
        status (Union[Unset, PostCreateRequestStatus]): * `draft` - Draft
            * `published` - Published
            * `archived` - Archived
        is_featured (Union[Unset, bool]):
        allow_comments (Union[Unset, bool]):
        meta_title (Union[Unset, str]):
        meta_description (Union[Unset, str]):
        meta_keywords (Union[Unset, str]):
        featured_image (Union[File, None, Unset]):
        featured_image_alt (Union[Unset, str]):
    """

    title: str
    content: str
    excerpt: Union[Unset, str] = UNSET
    category: Union[None, Unset, int] = UNSET
    tags: Union[Unset, list[int]] = UNSET
    status: Union[Unset, PostCreateRequestStatus] = UNSET
    is_featured: Union[Unset, bool] = UNSET
    allow_comments: Union[Unset, bool] = UNSET
    meta_title: Union[Unset, str] = UNSET
    meta_description: Union[Unset, str] = UNSET
    meta_keywords: Union[Unset, str] = UNSET
    featured_image: Union[File, None, Unset] = UNSET
    featured_image_alt: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        content = self.content

        excerpt = self.excerpt

        category: Union[None, Unset, int]
        if isinstance(self.category, Unset):
            category = UNSET
        else:
            category = self.category

        tags: Union[Unset, list[int]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

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

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "title": title,
                "content": content,
            }
        )
        if excerpt is not UNSET:
            field_dict["excerpt"] = excerpt
        if category is not UNSET:
            field_dict["category"] = category
        if tags is not UNSET:
            field_dict["tags"] = tags
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

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        files.append(("title", (None, str(self.title).encode(), "text/plain")))

        files.append(("content", (None, str(self.content).encode(), "text/plain")))

        if not isinstance(self.excerpt, Unset):
            files.append(("excerpt", (None, str(self.excerpt).encode(), "text/plain")))

        if not isinstance(self.category, Unset):
            if isinstance(self.category, int):
                files.append(("category", (None, str(self.category).encode(), "text/plain")))
            else:
                files.append(("category", (None, str(self.category).encode(), "text/plain")))

        if not isinstance(self.tags, Unset):
            for tags_item_element in self.tags:
                files.append(("tags", (None, str(tags_item_element).encode(), "text/plain")))

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

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        title = d.pop("title")

        content = d.pop("content")

        excerpt = d.pop("excerpt", UNSET)

        def _parse_category(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        category = _parse_category(d.pop("category", UNSET))

        tags = cast(list[int], d.pop("tags", UNSET))

        _status = d.pop("status", UNSET)
        status: Union[Unset, PostCreateRequestStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = check_post_create_request_status(_status)

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

        post_create_request = cls(
            title=title,
            content=content,
            excerpt=excerpt,
            category=category,
            tags=tags,
            status=status,
            is_featured=is_featured,
            allow_comments=allow_comments,
            meta_title=meta_title,
            meta_description=meta_description,
            meta_keywords=meta_keywords,
            featured_image=featured_image,
            featured_image_alt=featured_image_alt,
        )

        post_create_request.additional_properties = d
        return post_create_request

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
