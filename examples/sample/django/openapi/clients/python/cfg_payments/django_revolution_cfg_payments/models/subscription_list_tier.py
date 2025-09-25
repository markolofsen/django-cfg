from typing import Literal, cast

SubscriptionListTier = Literal["basic", "enterprise", "premium"]

SUBSCRIPTION_LIST_TIER_VALUES: set[SubscriptionListTier] = {
    "basic",
    "enterprise",
    "premium",
}


def check_subscription_list_tier(value: str) -> SubscriptionListTier:
    if value in SUBSCRIPTION_LIST_TIER_VALUES:
        return cast(SubscriptionListTier, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {SUBSCRIPTION_LIST_TIER_VALUES!r}")
