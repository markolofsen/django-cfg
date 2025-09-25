from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.transaction_list_transaction_type import check_transaction_list_transaction_type
from ..models.transaction_list_transaction_type import TransactionListTransactionType
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime


T = TypeVar("T", bound="TransactionList")


@_attrs_define
class TransactionList:
    """Simplified transaction for lists.

    Attributes:
        id (UUID): Unique identifier
        amount_usd (float): Transaction amount in USD (positive for credits, negative for debits)
        transaction_type (TransactionListTransactionType): Type of transaction

            * `payment` - Payment
            * `subscription` - Subscription
            * `refund` - Refund
            * `credit` - Credit
            * `debit` - Debit
            * `hold` - Hold
            * `release` - Release
            * `fee` - Fee
            * `adjustment` - Adjustment
        transaction_type_display (str):
        description (str): Human-readable description of the transaction
        balance_after (float): User balance after this transaction
        created_at (datetime.datetime):
    """

    id: UUID
    amount_usd: float
    transaction_type: TransactionListTransactionType
    transaction_type_display: str
    description: str
    balance_after: float
    created_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        amount_usd = self.amount_usd

        transaction_type: str = self.transaction_type

        transaction_type_display = self.transaction_type_display

        description = self.description

        balance_after = self.balance_after

        created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "amount_usd": amount_usd,
                "transaction_type": transaction_type,
                "transaction_type_display": transaction_type_display,
                "description": description,
                "balance_after": balance_after,
                "created_at": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        amount_usd = d.pop("amount_usd")

        transaction_type = check_transaction_list_transaction_type(d.pop("transaction_type"))

        transaction_type_display = d.pop("transaction_type_display")

        description = d.pop("description")

        balance_after = d.pop("balance_after")

        created_at = isoparse(d.pop("created_at"))

        transaction_list = cls(
            id=id,
            amount_usd=amount_usd,
            transaction_type=transaction_type,
            transaction_type_display=transaction_type_display,
            description=description,
            balance_after=balance_after,
            created_at=created_at,
        )

        transaction_list.additional_properties = d
        return transaction_list

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
