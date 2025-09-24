from typing import Literal, cast

PatchedUniversalPaymentRequestStatus = Literal[
    "cancelled", "completed", "confirmed", "confirming", "expired", "failed", "pending", "refunded"
]

PATCHED_UNIVERSAL_PAYMENT_REQUEST_STATUS_VALUES: set[PatchedUniversalPaymentRequestStatus] = {
    "cancelled",
    "completed",
    "confirmed",
    "confirming",
    "expired",
    "failed",
    "pending",
    "refunded",
}


def check_patched_universal_payment_request_status(value: str) -> PatchedUniversalPaymentRequestStatus:
    if value in PATCHED_UNIVERSAL_PAYMENT_REQUEST_STATUS_VALUES:
        return cast(PatchedUniversalPaymentRequestStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PATCHED_UNIVERSAL_PAYMENT_REQUEST_STATUS_VALUES!r}")
