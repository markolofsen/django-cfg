from typing import Literal, cast

SubscriptionCreateTier = Literal["basic", "enterprise", "premium"]

SUBSCRIPTION_CREATE_TIER_VALUES: set[SubscriptionCreateTier] = {
    "basic",
    "enterprise",
    "premium",
}


def check_subscription_create_tier(value: str) -> SubscriptionCreateTier:
    if value in SUBSCRIPTION_CREATE_TIER_VALUES:
        return cast(SubscriptionCreateTier, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {SUBSCRIPTION_CREATE_TIER_VALUES!r}")
