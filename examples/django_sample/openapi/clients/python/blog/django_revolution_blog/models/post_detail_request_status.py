from typing import Literal, cast

PostDetailRequestStatus = Literal["archived", "draft", "published"]

POST_DETAIL_REQUEST_STATUS_VALUES: set[PostDetailRequestStatus] = {
    "archived",
    "draft",
    "published",
}


def check_post_detail_request_status(value: str) -> PostDetailRequestStatus:
    if value in POST_DETAIL_REQUEST_STATUS_VALUES:
        return cast(PostDetailRequestStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {POST_DETAIL_REQUEST_STATUS_VALUES!r}")
