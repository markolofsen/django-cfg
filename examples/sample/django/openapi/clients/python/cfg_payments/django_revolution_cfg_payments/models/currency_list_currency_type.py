from typing import Literal, cast

CurrencyListCurrencyType = Literal["crypto", "fiat"]

CURRENCY_LIST_CURRENCY_TYPE_VALUES: set[CurrencyListCurrencyType] = {
    "crypto",
    "fiat",
}


def check_currency_list_currency_type(value: str) -> CurrencyListCurrencyType:
    if value in CURRENCY_LIST_CURRENCY_TYPE_VALUES:
        return cast(CurrencyListCurrencyType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {CURRENCY_LIST_CURRENCY_TYPE_VALUES!r}")
