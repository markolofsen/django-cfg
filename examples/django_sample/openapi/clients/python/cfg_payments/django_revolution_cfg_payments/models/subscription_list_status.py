from typing import Literal, cast

SubscriptionListStatus = Literal["active", "cancelled", "expired", "inactive", "suspended"]

SUBSCRIPTION_LIST_STATUS_VALUES: set[SubscriptionListStatus] = {
    "active",
    "cancelled",
    "expired",
    "inactive",
    "suspended",
}


def check_subscription_list_status(value: str) -> SubscriptionListStatus:
    if value in SUBSCRIPTION_LIST_STATUS_VALUES:
        return cast(SubscriptionListStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {SUBSCRIPTION_LIST_STATUS_VALUES!r}")
