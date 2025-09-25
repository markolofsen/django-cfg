from typing import Literal, cast

PatchedPostUpdateRequestStatus = Literal["archived", "draft", "published"]

PATCHED_POST_UPDATE_REQUEST_STATUS_VALUES: set[PatchedPostUpdateRequestStatus] = {
    "archived",
    "draft",
    "published",
}


def check_patched_post_update_request_status(value: str) -> PatchedPostUpdateRequestStatus:
    if value in PATCHED_POST_UPDATE_REQUEST_STATUS_VALUES:
        return cast(PatchedPostUpdateRequestStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PATCHED_POST_UPDATE_REQUEST_STATUS_VALUES!r}")
