from typing import Literal, cast

PaymentsPaymentsListProvider = Literal["internal", "nowpayments", "stripe"]

PAYMENTS_PAYMENTS_LIST_PROVIDER_VALUES: set[PaymentsPaymentsListProvider] = {
    "internal",
    "nowpayments",
    "stripe",
}


def check_payments_payments_list_provider(value: str) -> PaymentsPaymentsListProvider:
    if value in PAYMENTS_PAYMENTS_LIST_PROVIDER_VALUES:
        return cast(PaymentsPaymentsListProvider, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PAYMENTS_PAYMENTS_LIST_PROVIDER_VALUES!r}")
