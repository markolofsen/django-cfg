from typing import Literal, cast

PaymentsTransactionsListTransactionType = Literal[
    "adjustment", "credit", "debit", "fee", "hold", "payment", "refund", "release", "subscription"
]

PAYMENTS_TRANSACTIONS_LIST_TRANSACTION_TYPE_VALUES: set[PaymentsTransactionsListTransactionType] = {
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


def check_payments_transactions_list_transaction_type(value: str) -> PaymentsTransactionsListTransactionType:
    if value in PAYMENTS_TRANSACTIONS_LIST_TRANSACTION_TYPE_VALUES:
        return cast(PaymentsTransactionsListTransactionType, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {PAYMENTS_TRANSACTIONS_LIST_TRANSACTION_TYPE_VALUES!r}"
    )
