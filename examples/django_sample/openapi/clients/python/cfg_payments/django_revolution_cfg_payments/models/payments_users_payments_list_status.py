from typing import Literal, cast

PaymentsUsersPaymentsListStatus = Literal[
    "cancelled", "completed", "confirmed", "confirming", "expired", "failed", "pending", "refunded"
]

PAYMENTS_USERS_PAYMENTS_LIST_STATUS_VALUES: set[PaymentsUsersPaymentsListStatus] = {
    "cancelled",
    "completed",
    "confirmed",
    "confirming",
    "expired",
    "failed",
    "pending",
    "refunded",
}


def check_payments_users_payments_list_status(value: str) -> PaymentsUsersPaymentsListStatus:
    if value in PAYMENTS_USERS_PAYMENTS_LIST_STATUS_VALUES:
        return cast(PaymentsUsersPaymentsListStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PAYMENTS_USERS_PAYMENTS_LIST_STATUS_VALUES!r}")
