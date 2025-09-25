from typing import Literal, cast

UniversalPaymentStatus = Literal[
    "cancelled", "completed", "confirmed", "confirming", "expired", "failed", "pending", "refunded"
]

UNIVERSAL_PAYMENT_STATUS_VALUES: set[UniversalPaymentStatus] = {
    "cancelled",
    "completed",
    "confirmed",
    "confirming",
    "expired",
    "failed",
    "pending",
    "refunded",
}


def check_universal_payment_status(value: str) -> UniversalPaymentStatus:
    if value in UNIVERSAL_PAYMENT_STATUS_VALUES:
        return cast(UniversalPaymentStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {UNIVERSAL_PAYMENT_STATUS_VALUES!r}")
