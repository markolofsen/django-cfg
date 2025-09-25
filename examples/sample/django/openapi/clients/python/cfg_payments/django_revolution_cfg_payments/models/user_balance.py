from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
import datetime


T = TypeVar("T", bound="UserBalance")


@_attrs_define
class UserBalance:
    """User balance with computed fields.

    Attributes:
        total_balance (float): Get total balance (available + reserved).
        total_earned (float): Total amount earned (lifetime)
        total_spent (float): Total amount spent (lifetime)
        last_transaction_at (Union[None, datetime.datetime]): When the last transaction occurred
        pending_payments_count (str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        amount_usd (Union[Unset, float]): Current balance in USD
        reserved_usd (Union[Unset, float]): Reserved balance in USD (for pending transactions)
    """

    total_balance: float
    total_earned: float
    total_spent: float
    last_transaction_at: Union[None, datetime.datetime]
    pending_payments_count: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    amount_usd: Union[Unset, float] = UNSET
    reserved_usd: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_balance = self.total_balance

        total_earned = self.total_earned

        total_spent = self.total_spent

        last_transaction_at: Union[None, str]
        if isinstance(self.last_transaction_at, datetime.datetime):
            last_transaction_at = self.last_transaction_at.isoformat()
        else:
            last_transaction_at = self.last_transaction_at

        pending_payments_count = self.pending_payments_count

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        amount_usd = self.amount_usd

        reserved_usd = self.reserved_usd

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total_balance": total_balance,
                "total_earned": total_earned,
                "total_spent": total_spent,
                "last_transaction_at": last_transaction_at,
                "pending_payments_count": pending_payments_count,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if amount_usd is not UNSET:
            field_dict["amount_usd"] = amount_usd
        if reserved_usd is not UNSET:
            field_dict["reserved_usd"] = reserved_usd

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        total_balance = d.pop("total_balance")

        total_earned = d.pop("total_earned")

        total_spent = d.pop("total_spent")

        def _parse_last_transaction_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_transaction_at_type_0 = isoparse(data)

                return last_transaction_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        last_transaction_at = _parse_last_transaction_at(d.pop("last_transaction_at"))

        pending_payments_count = d.pop("pending_payments_count")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        amount_usd = d.pop("amount_usd", UNSET)

        reserved_usd = d.pop("reserved_usd", UNSET)

        user_balance = cls(
            total_balance=total_balance,
            total_earned=total_earned,
            total_spent=total_spent,
            last_transaction_at=last_transaction_at,
            pending_payments_count=pending_payments_count,
            created_at=created_at,
            updated_at=updated_at,
            amount_usd=amount_usd,
            reserved_usd=reserved_usd,
        )

        user_balance.additional_properties = d
        return user_balance

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
