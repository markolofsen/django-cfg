from typing import Literal, cast

UniversalPaymentProvider = Literal["internal", "nowpayments", "stripe"]

UNIVERSAL_PAYMENT_PROVIDER_VALUES: set[UniversalPaymentProvider] = {
    "internal",
    "nowpayments",
    "stripe",
}


def check_universal_payment_provider(value: str) -> UniversalPaymentProvider:
    if value in UNIVERSAL_PAYMENT_PROVIDER_VALUES:
        return cast(UniversalPaymentProvider, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {UNIVERSAL_PAYMENT_PROVIDER_VALUES!r}")
