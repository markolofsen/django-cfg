from typing import Literal, cast

UniversalPaymentRequestStatus = Literal[
    "cancelled", "completed", "confirmed", "confirming", "expired", "failed", "pending", "refunded"
]

UNIVERSAL_PAYMENT_REQUEST_STATUS_VALUES: set[UniversalPaymentRequestStatus] = {
    "cancelled",
    "completed",
    "confirmed",
    "confirming",
    "expired",
    "failed",
    "pending",
    "refunded",
}


def check_universal_payment_request_status(value: str) -> UniversalPaymentRequestStatus:
    if value in UNIVERSAL_PAYMENT_REQUEST_STATUS_VALUES:
        return cast(UniversalPaymentRequestStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {UNIVERSAL_PAYMENT_REQUEST_STATUS_VALUES!r}")
