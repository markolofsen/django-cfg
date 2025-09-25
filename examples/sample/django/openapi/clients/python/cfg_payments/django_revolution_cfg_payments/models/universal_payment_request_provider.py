from typing import Literal, cast

UniversalPaymentRequestProvider = Literal["internal", "nowpayments", "stripe"]

UNIVERSAL_PAYMENT_REQUEST_PROVIDER_VALUES: set[UniversalPaymentRequestProvider] = {
    "internal",
    "nowpayments",
    "stripe",
}


def check_universal_payment_request_provider(value: str) -> UniversalPaymentRequestProvider:
    if value in UNIVERSAL_PAYMENT_REQUEST_PROVIDER_VALUES:
        return cast(UniversalPaymentRequestProvider, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {UNIVERSAL_PAYMENT_REQUEST_PROVIDER_VALUES!r}")
