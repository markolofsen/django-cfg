from typing import Literal, cast

SubscriptionTier = Literal["basic", "enterprise", "premium"]

SUBSCRIPTION_TIER_VALUES: set[SubscriptionTier] = {
    "basic",
    "enterprise",
    "premium",
}


def check_subscription_tier(value: str) -> SubscriptionTier:
    if value in SUBSCRIPTION_TIER_VALUES:
        return cast(SubscriptionTier, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {SUBSCRIPTION_TIER_VALUES!r}")
