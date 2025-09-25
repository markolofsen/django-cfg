from typing import Literal, cast

PaymentsUsersSubscriptionsListTier = Literal["basic", "enterprise", "premium"]

PAYMENTS_USERS_SUBSCRIPTIONS_LIST_TIER_VALUES: set[PaymentsUsersSubscriptionsListTier] = {
    "basic",
    "enterprise",
    "premium",
}


def check_payments_users_subscriptions_list_tier(value: str) -> PaymentsUsersSubscriptionsListTier:
    if value in PAYMENTS_USERS_SUBSCRIPTIONS_LIST_TIER_VALUES:
        return cast(PaymentsUsersSubscriptionsListTier, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PAYMENTS_USERS_SUBSCRIPTIONS_LIST_TIER_VALUES!r}")
