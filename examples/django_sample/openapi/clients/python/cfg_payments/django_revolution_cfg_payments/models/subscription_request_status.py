from typing import Literal, cast

SubscriptionRequestStatus = Literal["active", "cancelled", "expired", "inactive", "suspended"]

SUBSCRIPTION_REQUEST_STATUS_VALUES: set[SubscriptionRequestStatus] = {
    "active",
    "cancelled",
    "expired",
    "inactive",
    "suspended",
}


def check_subscription_request_status(value: str) -> SubscriptionRequestStatus:
    if value in SUBSCRIPTION_REQUEST_STATUS_VALUES:
        return cast(SubscriptionRequestStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {SUBSCRIPTION_REQUEST_STATUS_VALUES!r}")
