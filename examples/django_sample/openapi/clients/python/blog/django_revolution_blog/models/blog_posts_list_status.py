from typing import Literal, cast

BlogPostsListStatus = Literal["archived", "draft", "published"]

BLOG_POSTS_LIST_STATUS_VALUES: set[BlogPostsListStatus] = {
    "archived",
    "draft",
    "published",
}


def check_blog_posts_list_status(value: str) -> BlogPostsListStatus:
    if value in BLOG_POSTS_LIST_STATUS_VALUES:
        return cast(BlogPostsListStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {BLOG_POSTS_LIST_STATUS_VALUES!r}")
