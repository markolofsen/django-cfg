from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
    from ..models.post_list import PostList
    from ..models.tag import Tag
    from ..models.category import Category


T = TypeVar("T", bound="BlogStats")


@_attrs_define
class BlogStats:
    """Serializer for blog statistics.

    Attributes:
        total_posts (int):
        published_posts (int):
        draft_posts (int):
        total_comments (int):
        total_views (int):
        total_likes (int):
        popular_posts (list['PostList']):
        recent_posts (list['PostList']):
        top_categories (list['Category']):
        top_tags (list['Tag']):
    """

    total_posts: int
    published_posts: int
    draft_posts: int
    total_comments: int
    total_views: int
    total_likes: int
    popular_posts: list["PostList"]
    recent_posts: list["PostList"]
    top_categories: list["Category"]
    top_tags: list["Tag"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.post_list import PostList
        from ..models.tag import Tag
        from ..models.category import Category

        total_posts = self.total_posts

        published_posts = self.published_posts

        draft_posts = self.draft_posts

        total_comments = self.total_comments

        total_views = self.total_views

        total_likes = self.total_likes

        popular_posts = []
        for popular_posts_item_data in self.popular_posts:
            popular_posts_item = popular_posts_item_data.to_dict()
            popular_posts.append(popular_posts_item)

        recent_posts = []
        for recent_posts_item_data in self.recent_posts:
            recent_posts_item = recent_posts_item_data.to_dict()
            recent_posts.append(recent_posts_item)

        top_categories = []
        for top_categories_item_data in self.top_categories:
            top_categories_item = top_categories_item_data.to_dict()
            top_categories.append(top_categories_item)

        top_tags = []
        for top_tags_item_data in self.top_tags:
            top_tags_item = top_tags_item_data.to_dict()
            top_tags.append(top_tags_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total_posts": total_posts,
                "published_posts": published_posts,
                "draft_posts": draft_posts,
                "total_comments": total_comments,
                "total_views": total_views,
                "total_likes": total_likes,
                "popular_posts": popular_posts,
                "recent_posts": recent_posts,
                "top_categories": top_categories,
                "top_tags": top_tags,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_list import PostList
        from ..models.tag import Tag
        from ..models.category import Category

        d = dict(src_dict)
        total_posts = d.pop("total_posts")

        published_posts = d.pop("published_posts")

        draft_posts = d.pop("draft_posts")

        total_comments = d.pop("total_comments")

        total_views = d.pop("total_views")

        total_likes = d.pop("total_likes")

        popular_posts = []
        _popular_posts = d.pop("popular_posts")
        for popular_posts_item_data in _popular_posts:
            popular_posts_item = PostList.from_dict(popular_posts_item_data)

            popular_posts.append(popular_posts_item)

        recent_posts = []
        _recent_posts = d.pop("recent_posts")
        for recent_posts_item_data in _recent_posts:
            recent_posts_item = PostList.from_dict(recent_posts_item_data)

            recent_posts.append(recent_posts_item)

        top_categories = []
        _top_categories = d.pop("top_categories")
        for top_categories_item_data in _top_categories:
            top_categories_item = Category.from_dict(top_categories_item_data)

            top_categories.append(top_categories_item)

        top_tags = []
        _top_tags = d.pop("top_tags")
        for top_tags_item_data in _top_tags:
            top_tags_item = Tag.from_dict(top_tags_item_data)

            top_tags.append(top_tags_item)

        blog_stats = cls(
            total_posts=total_posts,
            published_posts=published_posts,
            draft_posts=draft_posts,
            total_comments=total_comments,
            total_views=total_views,
            total_likes=total_likes,
            popular_posts=popular_posts,
            recent_posts=recent_posts,
            top_categories=top_categories,
            top_tags=top_tags,
        )

        blog_stats.additional_properties = d
        return blog_stats

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
