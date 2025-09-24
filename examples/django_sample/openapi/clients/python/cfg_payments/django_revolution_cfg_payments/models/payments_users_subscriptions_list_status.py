from typing import Literal, cast

PaymentsUsersSubscriptionsListStatus = Literal["active", "cancelled", "expired", "inactive", "suspended"]

PAYMENTS_USERS_SUBSCRIPTIONS_LIST_STATUS_VALUES: set[PaymentsUsersSubscriptionsListStatus] = {
    "active",
    "cancelled",
    "expired",
    "inactive",
    "suspended",
}


def check_payments_users_subscriptions_list_status(value: str) -> PaymentsUsersSubscriptionsListStatus:
    if value in PAYMENTS_USERS_SUBSCRIPTIONS_LIST_STATUS_VALUES:
        return cast(PaymentsUsersSubscriptionsListStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PAYMENTS_USERS_SUBSCRIPTIONS_LIST_STATUS_VALUES!r}")
