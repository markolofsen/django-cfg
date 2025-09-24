from typing import Literal, cast

PaymentsSubscriptionsListStatus = Literal["active", "cancelled", "expired", "inactive", "suspended"]

PAYMENTS_SUBSCRIPTIONS_LIST_STATUS_VALUES: set[PaymentsSubscriptionsListStatus] = {
    "active",
    "cancelled",
    "expired",
    "inactive",
    "suspended",
}


def check_payments_subscriptions_list_status(value: str) -> PaymentsSubscriptionsListStatus:
    if value in PAYMENTS_SUBSCRIPTIONS_LIST_STATUS_VALUES:
        return cast(PaymentsSubscriptionsListStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PAYMENTS_SUBSCRIPTIONS_LIST_STATUS_VALUES!r}")
