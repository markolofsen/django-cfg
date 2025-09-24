from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.transaction_transaction_type import check_transaction_transaction_type
from ..models.transaction_transaction_type import TransactionTransactionType
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
from uuid import UUID
import datetime


T = TypeVar("T", bound="Transaction")


@_attrs_define
class Transaction:
    """Transaction with details.

    Attributes:
        id (UUID): Unique identifier
        amount_usd (float): Transaction amount in USD (positive for credits, negative for debits)
        transaction_type (TransactionTransactionType): Type of transaction

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
        balance_before (float): User balance before this transaction
        balance_after (float): User balance after this transaction
        is_credit (bool): Check if this is a credit transaction.
        is_debit (bool): Check if this is a debit transaction.
        created_at (datetime.datetime):
        reference_id (Union[None, Unset, str]): External reference ID
    """

    id: UUID
    amount_usd: float
    transaction_type: TransactionTransactionType
    transaction_type_display: str
    description: str
    balance_before: float
    balance_after: float
    is_credit: bool
    is_debit: bool
    created_at: datetime.datetime
    reference_id: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        amount_usd = self.amount_usd

        transaction_type: str = self.transaction_type

        transaction_type_display = self.transaction_type_display

        description = self.description

        balance_before = self.balance_before

        balance_after = self.balance_after

        is_credit = self.is_credit

        is_debit = self.is_debit

        created_at = self.created_at.isoformat()

        reference_id: Union[None, Unset, str]
        if isinstance(self.reference_id, Unset):
            reference_id = UNSET
        else:
            reference_id = self.reference_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "amount_usd": amount_usd,
                "transaction_type": transaction_type,
                "transaction_type_display": transaction_type_display,
                "description": description,
                "balance_before": balance_before,
                "balance_after": balance_after,
                "is_credit": is_credit,
                "is_debit": is_debit,
                "created_at": created_at,
            }
        )
        if reference_id is not UNSET:
            field_dict["reference_id"] = reference_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        amount_usd = d.pop("amount_usd")

        transaction_type = check_transaction_transaction_type(d.pop("transaction_type"))

        transaction_type_display = d.pop("transaction_type_display")

        description = d.pop("description")

        balance_before = d.pop("balance_before")

        balance_after = d.pop("balance_after")

        is_credit = d.pop("is_credit")

        is_debit = d.pop("is_debit")

        created_at = isoparse(d.pop("created_at"))

        def _parse_reference_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        reference_id = _parse_reference_id(d.pop("reference_id", UNSET))

        transaction = cls(
            id=id,
            amount_usd=amount_usd,
            transaction_type=transaction_type,
            transaction_type_display=transaction_type_display,
            description=description,
            balance_before=balance_before,
            balance_after=balance_after,
            is_credit=is_credit,
            is_debit=is_debit,
            created_at=created_at,
            reference_id=reference_id,
        )

        transaction.additional_properties = d
        return transaction

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
