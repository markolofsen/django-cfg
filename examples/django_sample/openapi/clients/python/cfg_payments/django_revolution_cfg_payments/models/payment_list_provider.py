from typing import Literal, cast

PaymentListProvider = Literal["internal", "nowpayments", "stripe"]

PAYMENT_LIST_PROVIDER_VALUES: set[PaymentListProvider] = {
    "internal",
    "nowpayments",
    "stripe",
}


def check_payment_list_provider(value: str) -> PaymentListProvider:
    if value in PAYMENT_LIST_PROVIDER_VALUES:
        return cast(PaymentListProvider, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PAYMENT_LIST_PROVIDER_VALUES!r}")
