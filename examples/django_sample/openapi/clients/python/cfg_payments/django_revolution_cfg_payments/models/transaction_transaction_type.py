from typing import Literal, cast

TransactionTransactionType = Literal[
    "adjustment", "credit", "debit", "fee", "hold", "payment", "refund", "release", "subscription"
]

TRANSACTION_TRANSACTION_TYPE_VALUES: set[TransactionTransactionType] = {
    "adjustment",
    "credit",
    "debit",
    "fee",
    "hold",
    "payment",
    "refund",
    "release",
    "subscription",
}


def check_transaction_transaction_type(value: str) -> TransactionTransactionType:
    if value in TRANSACTION_TRANSACTION_TYPE_VALUES:
        return cast(TransactionTransactionType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TRANSACTION_TRANSACTION_TYPE_VALUES!r}")
