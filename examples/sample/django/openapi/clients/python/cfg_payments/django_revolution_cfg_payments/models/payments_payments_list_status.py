from typing import Literal, cast

PaymentsPaymentsListStatus = Literal[
    "cancelled", "completed", "confirmed", "confirming", "expired", "failed", "pending", "refunded"
]

PAYMENTS_PAYMENTS_LIST_STATUS_VALUES: set[PaymentsPaymentsListStatus] = {
    "cancelled",
    "completed",
    "confirmed",
    "confirming",
    "expired",
    "failed",
    "pending",
    "refunded",
}


def check_payments_payments_list_status(value: str) -> PaymentsPaymentsListStatus:
    if value in PAYMENTS_PAYMENTS_LIST_STATUS_VALUES:
        return cast(PaymentsPaymentsListStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PAYMENTS_PAYMENTS_LIST_STATUS_VALUES!r}")
