from typing import Literal, cast

PaymentsSubscriptionsListTier = Literal["basic", "enterprise", "premium"]

PAYMENTS_SUBSCRIPTIONS_LIST_TIER_VALUES: set[PaymentsSubscriptionsListTier] = {
    "basic",
    "enterprise",
    "premium",
}


def check_payments_subscriptions_list_tier(value: str) -> PaymentsSubscriptionsListTier:
    if value in PAYMENTS_SUBSCRIPTIONS_LIST_TIER_VALUES:
        return cast(PaymentsSubscriptionsListTier, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PAYMENTS_SUBSCRIPTIONS_LIST_TIER_VALUES!r}")
