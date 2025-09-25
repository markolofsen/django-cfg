from typing import Literal, cast

SubscriptionStatus = Literal["active", "cancelled", "expired", "inactive", "suspended"]

SUBSCRIPTION_STATUS_VALUES: set[SubscriptionStatus] = {
    "active",
    "cancelled",
    "expired",
    "inactive",
    "suspended",
}


def check_subscription_status(value: str) -> SubscriptionStatus:
    if value in SUBSCRIPTION_STATUS_VALUES:
        return cast(SubscriptionStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {SUBSCRIPTION_STATUS_VALUES!r}")
