from typing import Literal, cast

SubscriptionRequestTier = Literal["basic", "enterprise", "premium"]

SUBSCRIPTION_REQUEST_TIER_VALUES: set[SubscriptionRequestTier] = {
    "basic",
    "enterprise",
    "premium",
}


def check_subscription_request_tier(value: str) -> SubscriptionRequestTier:
    if value in SUBSCRIPTION_REQUEST_TIER_VALUES:
        return cast(SubscriptionRequestTier, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {SUBSCRIPTION_REQUEST_TIER_VALUES!r}")
