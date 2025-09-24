from typing import Literal, cast

PostCreateStatus = Literal["archived", "draft", "published"]

POST_CREATE_STATUS_VALUES: set[PostCreateStatus] = {
    "archived",
    "draft",
    "published",
}


def check_post_create_status(value: str) -> PostCreateStatus:
    if value in POST_CREATE_STATUS_VALUES:
        return cast(PostCreateStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {POST_CREATE_STATUS_VALUES!r}")
