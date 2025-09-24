from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.payment_list_provider import check_payment_list_provider
from ..models.payment_list_provider import PaymentListProvider
from ..models.payment_list_status import check_payment_list_status
from ..models.payment_list_status import PaymentListStatus
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import Union
from uuid import UUID
import datetime


T = TypeVar("T", bound="PaymentList")


@_attrs_define
class PaymentList:
    """Simplified payment for lists.

    Attributes:
        id (UUID): Unique identifier
        internal_payment_id (str): Internal payment identifier
        amount_usd (float): Payment amount in USD
        currency_code (str): Currency used for payment
        provider (PaymentListProvider): Payment provider

            * `nowpayments` - NowPayments
            * `stripe` - Stripe
            * `internal` - Internal
        status_display (str):
        created_at (datetime.datetime):
        status (Union[Unset, PaymentListStatus]): Payment status

            * `pending` - Pending
            * `confirming` - Confirming
            * `confirmed` - Confirmed
            * `completed` - Completed
            * `failed` - Failed
            * `expired` - Expired
            * `cancelled` - Cancelled
            * `refunded` - Refunded
        description (Union[Unset, str]): Payment description
    """

    id: UUID
    internal_payment_id: str
    amount_usd: float
    currency_code: str
    provider: PaymentListProvider
    status_display: str
    created_at: datetime.datetime
    status: Union[Unset, PaymentListStatus] = UNSET
    description: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        internal_payment_id = self.internal_payment_id

        amount_usd = self.amount_usd

        currency_code = self.currency_code

        provider: str = self.provider

        status_display = self.status_display

        created_at = self.created_at.isoformat()

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "internal_payment_id": internal_payment_id,
                "amount_usd": amount_usd,
                "currency_code": currency_code,
                "provider": provider,
                "status_display": status_display,
                "created_at": created_at,
            }
        )
        if status is not UNSET:
            field_dict["status"] = status
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        internal_payment_id = d.pop("internal_payment_id")

        amount_usd = d.pop("amount_usd")

        currency_code = d.pop("currency_code")

        provider = check_payment_list_provider(d.pop("provider"))

        status_display = d.pop("status_display")

        created_at = isoparse(d.pop("created_at"))

        _status = d.pop("status", UNSET)
        status: Union[Unset, PaymentListStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = check_payment_list_status(_status)

        description = d.pop("description", UNSET)

        payment_list = cls(
            id=id,
            internal_payment_id=internal_payment_id,
            amount_usd=amount_usd,
            currency_code=currency_code,
            provider=provider,
            status_display=status_display,
            created_at=created_at,
            status=status,
            description=description,
        )

        payment_list.additional_properties = d
        return payment_list

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
