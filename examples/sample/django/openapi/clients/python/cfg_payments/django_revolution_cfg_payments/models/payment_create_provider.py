from typing import Literal, cast

PaymentCreateProvider = Literal["internal", "nowpayments", "stripe"]

PAYMENT_CREATE_PROVIDER_VALUES: set[PaymentCreateProvider] = {
    "internal",
    "nowpayments",
    "stripe",
}


def check_payment_create_provider(value: str) -> PaymentCreateProvider:
    if value in PAYMENT_CREATE_PROVIDER_VALUES:
        return cast(PaymentCreateProvider, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PAYMENT_CREATE_PROVIDER_VALUES!r}")
