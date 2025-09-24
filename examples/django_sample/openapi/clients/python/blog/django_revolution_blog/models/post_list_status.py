from typing import Literal, cast

PostListStatus = Literal["archived", "draft", "published"]

POST_LIST_STATUS_VALUES: set[PostListStatus] = {
    "archived",
    "draft",
    "published",
}


def check_post_list_status(value: str) -> PostListStatus:
    if value in POST_LIST_STATUS_VALUES:
        return cast(PostListStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {POST_LIST_STATUS_VALUES!r}")
