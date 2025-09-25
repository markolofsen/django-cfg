from typing import Literal, cast

PaymentCreateRequestProvider = Literal["internal", "nowpayments", "stripe"]

PAYMENT_CREATE_REQUEST_PROVIDER_VALUES: set[PaymentCreateRequestProvider] = {
    "internal",
    "nowpayments",
    "stripe",
}


def check_payment_create_request_provider(value: str) -> PaymentCreateRequestProvider:
    if value in PAYMENT_CREATE_REQUEST_PROVIDER_VALUES:
        return cast(PaymentCreateRequestProvider, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PAYMENT_CREATE_REQUEST_PROVIDER_VALUES!r}")
