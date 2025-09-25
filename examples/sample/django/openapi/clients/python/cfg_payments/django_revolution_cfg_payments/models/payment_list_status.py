from typing import Literal, cast

PaymentListStatus = Literal[
    "cancelled", "completed", "confirmed", "confirming", "expired", "failed", "pending", "refunded"
]

PAYMENT_LIST_STATUS_VALUES: set[PaymentListStatus] = {
    "cancelled",
    "completed",
    "confirmed",
    "confirming",
    "expired",
    "failed",
    "pending",
    "refunded",
}


def check_payment_list_status(value: str) -> PaymentListStatus:
    if value in PAYMENT_LIST_STATUS_VALUES:
        return cast(PaymentListStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PAYMENT_LIST_STATUS_VALUES!r}")
