from typing import Literal, cast

PaymentsUsersPaymentsListProvider = Literal["internal", "nowpayments", "stripe"]

PAYMENTS_USERS_PAYMENTS_LIST_PROVIDER_VALUES: set[PaymentsUsersPaymentsListProvider] = {
    "internal",
    "nowpayments",
    "stripe",
}


def check_payments_users_payments_list_provider(value: str) -> PaymentsUsersPaymentsListProvider:
    if value in PAYMENTS_USERS_PAYMENTS_LIST_PROVIDER_VALUES:
        return cast(PaymentsUsersPaymentsListProvider, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PAYMENTS_USERS_PAYMENTS_LIST_PROVIDER_VALUES!r}")
