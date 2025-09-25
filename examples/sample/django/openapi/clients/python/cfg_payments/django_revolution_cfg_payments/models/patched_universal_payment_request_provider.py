from typing import Literal, cast

PatchedUniversalPaymentRequestProvider = Literal["internal", "nowpayments", "stripe"]

PATCHED_UNIVERSAL_PAYMENT_REQUEST_PROVIDER_VALUES: set[PatchedUniversalPaymentRequestProvider] = {
    "internal",
    "nowpayments",
    "stripe",
}


def check_patched_universal_payment_request_provider(value: str) -> PatchedUniversalPaymentRequestProvider:
    if value in PATCHED_UNIVERSAL_PAYMENT_REQUEST_PROVIDER_VALUES:
        return cast(PatchedUniversalPaymentRequestProvider, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {PATCHED_UNIVERSAL_PAYMENT_REQUEST_PROVIDER_VALUES!r}"
    )
