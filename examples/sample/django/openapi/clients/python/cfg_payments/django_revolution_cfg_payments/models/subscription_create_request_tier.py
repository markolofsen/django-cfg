from typing import Literal, cast

SubscriptionCreateRequestTier = Literal["basic", "enterprise", "premium"]

SUBSCRIPTION_CREATE_REQUEST_TIER_VALUES: set[SubscriptionCreateRequestTier] = {
    "basic",
    "enterprise",
    "premium",
}


def check_subscription_create_request_tier(value: str) -> SubscriptionCreateRequestTier:
    if value in SUBSCRIPTION_CREATE_REQUEST_TIER_VALUES:
        return cast(SubscriptionCreateRequestTier, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {SUBSCRIPTION_CREATE_REQUEST_TIER_VALUES!r}")
