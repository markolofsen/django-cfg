from typing import Literal, cast

PostUpdateRequestStatus = Literal["archived", "draft", "published"]

POST_UPDATE_REQUEST_STATUS_VALUES: set[PostUpdateRequestStatus] = {
    "archived",
    "draft",
    "published",
}


def check_post_update_request_status(value: str) -> PostUpdateRequestStatus:
    if value in POST_UPDATE_REQUEST_STATUS_VALUES:
        return cast(PostUpdateRequestStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {POST_UPDATE_REQUEST_STATUS_VALUES!r}")
