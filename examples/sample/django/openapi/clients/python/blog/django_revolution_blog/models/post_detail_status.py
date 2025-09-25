from typing import Literal, cast

PostDetailStatus = Literal["archived", "draft", "published"]

POST_DETAIL_STATUS_VALUES: set[PostDetailStatus] = {
    "archived",
    "draft",
    "published",
}


def check_post_detail_status(value: str) -> PostDetailStatus:
    if value in POST_DETAIL_STATUS_VALUES:
        return cast(PostDetailStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {POST_DETAIL_STATUS_VALUES!r}")
