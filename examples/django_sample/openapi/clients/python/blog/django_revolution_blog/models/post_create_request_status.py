from typing import Literal, cast

PostCreateRequestStatus = Literal["archived", "draft", "published"]

POST_CREATE_REQUEST_STATUS_VALUES: set[PostCreateRequestStatus] = {
    "archived",
    "draft",
    "published",
}


def check_post_create_request_status(value: str) -> PostCreateRequestStatus:
    if value in POST_CREATE_REQUEST_STATUS_VALUES:
        return cast(PostCreateRequestStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {POST_CREATE_REQUEST_STATUS_VALUES!r}")
