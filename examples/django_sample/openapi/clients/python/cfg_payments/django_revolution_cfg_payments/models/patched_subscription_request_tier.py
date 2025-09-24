from typing import Literal, cast

PatchedSubscriptionRequestTier = Literal["basic", "enterprise", "premium"]

PATCHED_SUBSCRIPTION_REQUEST_TIER_VALUES: set[PatchedSubscriptionRequestTier] = {
    "basic",
    "enterprise",
    "premium",
}


def check_patched_subscription_request_tier(value: str) -> PatchedSubscriptionRequestTier:
    if value in PATCHED_SUBSCRIPTION_REQUEST_TIER_VALUES:
        return cast(PatchedSubscriptionRequestTier, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PATCHED_SUBSCRIPTION_REQUEST_TIER_VALUES!r}")
