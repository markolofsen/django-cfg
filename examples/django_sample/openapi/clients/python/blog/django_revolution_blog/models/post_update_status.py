from typing import Literal, cast

PostUpdateStatus = Literal["archived", "draft", "published"]

POST_UPDATE_STATUS_VALUES: set[PostUpdateStatus] = {
    "archived",
    "draft",
    "published",
}


def check_post_update_status(value: str) -> PostUpdateStatus:
    if value in POST_UPDATE_STATUS_VALUES:
        return cast(PostUpdateStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {POST_UPDATE_STATUS_VALUES!r}")
