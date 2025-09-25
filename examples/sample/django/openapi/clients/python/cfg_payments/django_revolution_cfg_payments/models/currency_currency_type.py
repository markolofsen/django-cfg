from typing import Literal, cast

CurrencyCurrencyType = Literal["crypto", "fiat"]

CURRENCY_CURRENCY_TYPE_VALUES: set[CurrencyCurrencyType] = {
    "crypto",
    "fiat",
}


def check_currency_currency_type(value: str) -> CurrencyCurrencyType:
    if value in CURRENCY_CURRENCY_TYPE_VALUES:
        return cast(CurrencyCurrencyType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {CURRENCY_CURRENCY_TYPE_VALUES!r}")
