from typing import Literal, cast

PaymentsCurrenciesListCurrencyType = Literal["crypto", "fiat"]

PAYMENTS_CURRENCIES_LIST_CURRENCY_TYPE_VALUES: set[PaymentsCurrenciesListCurrencyType] = {
    "crypto",
    "fiat",
}


def check_payments_currencies_list_currency_type(value: str) -> PaymentsCurrenciesListCurrencyType:
    if value in PAYMENTS_CURRENCIES_LIST_CURRENCY_TYPE_VALUES:
        return cast(PaymentsCurrenciesListCurrencyType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PAYMENTS_CURRENCIES_LIST_CURRENCY_TYPE_VALUES!r}")
