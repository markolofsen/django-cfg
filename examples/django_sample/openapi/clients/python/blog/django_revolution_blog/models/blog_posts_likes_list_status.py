from typing import Literal, cast

BlogPostsLikesListStatus = Literal["archived", "draft", "published"]

BLOG_POSTS_LIKES_LIST_STATUS_VALUES: set[BlogPostsLikesListStatus] = {
    "archived",
    "draft",
    "published",
}


def check_blog_posts_likes_list_status(value: str) -> BlogPostsLikesListStatus:
    if value in BLOG_POSTS_LIKES_LIST_STATUS_VALUES:
        return cast(BlogPostsLikesListStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {BLOG_POSTS_LIKES_LIST_STATUS_VALUES!r}")
