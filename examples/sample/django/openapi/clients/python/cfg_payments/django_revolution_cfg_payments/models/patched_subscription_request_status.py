from typing import Literal, cast

PatchedSubscriptionRequestStatus = Literal["active", "cancelled", "expired", "inactive", "suspended"]

PATCHED_SUBSCRIPTION_REQUEST_STATUS_VALUES: set[PatchedSubscriptionRequestStatus] = {
    "active",
    "cancelled",
    "expired",
    "inactive",
    "suspended",
}


def check_patched_subscription_request_status(value: str) -> PatchedSubscriptionRequestStatus:
    if value in PATCHED_SUBSCRIPTION_REQUEST_STATUS_VALUES:
        return cast(PatchedSubscriptionRequestStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PATCHED_SUBSCRIPTION_REQUEST_STATUS_VALUES!r}")
