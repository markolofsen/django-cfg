from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union

if TYPE_CHECKING:
    from ..models.comment import Comment


T = TypeVar("T", bound="PaginatedCommentList")


@_attrs_define
class PaginatedCommentList:
    """
    Attributes:
        count (int): Total number of items across all pages Example: 150.
        page (int): Current page number (1-based) Example: 2.
        pages (int): Total number of pages Example: 15.
        page_size (int): Number of items per page Example: 10.
        has_next (bool): Whether there is a next page Example: True.
        has_previous (bool): Whether there is a previous page Example: True.
        results (list['Comment']): Array of items for current page
        next_page (Union[None, Unset, int]): Next page number (null if no next page) Example: 3.
        previous_page (Union[None, Unset, int]): Previous page number (null if no previous page) Example: 1.
    """

    count: int
    page: int
    pages: int
    page_size: int
    has_next: bool
    has_previous: bool
    results: list["Comment"]
    next_page: Union[None, Unset, int] = UNSET
    previous_page: Union[None, Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.comment import Comment

        count = self.count

        page = self.page

        pages = self.pages

        page_size = self.page_size

        has_next = self.has_next

        has_previous = self.has_previous

        results = []
        for results_item_data in self.results:
            results_item = results_item_data.to_dict()
            results.append(results_item)

        next_page: Union[None, Unset, int]
        if isinstance(self.next_page, Unset):
            next_page = UNSET
        else:
            next_page = self.next_page

        previous_page: Union[None, Unset, int]
        if isinstance(self.previous_page, Unset):
            previous_page = UNSET
        else:
            previous_page = self.previous_page

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "count": count,
                "page": page,
                "pages": pages,
                "page_size": page_size,
                "has_next": has_next,
                "has_previous": has_previous,
                "results": results,
            }
        )
        if next_page is not UNSET:
            field_dict["next_page"] = next_page
        if previous_page is not UNSET:
            field_dict["previous_page"] = previous_page

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.comment import Comment

        d = dict(src_dict)
        count = d.pop("count")

        page = d.pop("page")

        pages = d.pop("pages")

        page_size = d.pop("page_size")

        has_next = d.pop("has_next")

        has_previous = d.pop("has_previous")

        results = []
        _results = d.pop("results")
        for results_item_data in _results:
            results_item = Comment.from_dict(results_item_data)

            results.append(results_item)

        def _parse_next_page(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        next_page = _parse_next_page(d.pop("next_page", UNSET))

        def _parse_previous_page(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        previous_page = _parse_previous_page(d.pop("previous_page", UNSET))

        paginated_comment_list = cls(
            count=count,
            page=page,
            pages=pages,
            page_size=page_size,
            has_next=has_next,
            has_previous=has_previous,
            results=results,
            next_page=next_page,
            previous_page=previous_page,
        )

        paginated_comment_list.additional_properties = d
        return paginated_comment_list

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
