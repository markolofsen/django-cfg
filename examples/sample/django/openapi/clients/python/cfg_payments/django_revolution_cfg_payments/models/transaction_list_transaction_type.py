from typing import Literal, cast

TransactionListTransactionType = Literal[
    "adjustment", "credit", "debit", "fee", "hold", "payment", "refund", "release", "subscription"
]

TRANSACTION_LIST_TRANSACTION_TYPE_VALUES: set[TransactionListTransactionType] = {
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


def check_transaction_list_transaction_type(value: str) -> TransactionListTransactionType:
    if value in TRANSACTION_LIST_TRANSACTION_TYPE_VALUES:
        return cast(TransactionListTransactionType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TRANSACTION_LIST_TRANSACTION_TYPE_VALUES!r}")
