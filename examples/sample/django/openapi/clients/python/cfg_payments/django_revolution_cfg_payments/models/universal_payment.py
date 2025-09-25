from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.universal_payment_provider import check_universal_payment_provider
from ..models.universal_payment_provider import UniversalPaymentProvider
from ..models.universal_payment_status import check_universal_payment_status
from ..models.universal_payment_status import UniversalPaymentStatus
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
from uuid import UUID
import datetime


T = TypeVar("T", bound="UniversalPayment")


@_attrs_define
class UniversalPayment:
    """Universal payment with status info.

    Attributes:
        id (UUID): Unique identifier
        internal_payment_id (str): Internal payment identifier
        provider_payment_id (Union[None, str]): Provider's payment ID
        amount_usd (float): Payment amount in USD
        currency_code (str): Currency used for payment
        actual_amount_usd (Union[None, float]): Actual received amount in USD
        actual_currency_code (Union[None, str]): Actual received currency
        fee_amount_usd (Union[None, float]): Fee amount in USD
        provider (UniversalPaymentProvider): Payment provider

            * `nowpayments` - NowPayments
            * `stripe` - Stripe
            * `internal` - Internal
        provider_display (str):
        status_display (str):
        pay_address (Union[None, str]): Cryptocurrency payment address
        pay_amount (Union[None, float]): Amount to pay in cryptocurrency
        is_pending (bool): Check if payment is still pending.
        is_completed (bool): Check if payment is completed.
        is_failed (bool): Check if payment failed.
        completed_at (Union[None, datetime.datetime]): Payment completion time
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        order_id (Union[None, Unset, str]): Order reference ID
        status (Union[Unset, UniversalPaymentStatus]): Payment status

            * `pending` - Pending
            * `confirming` - Confirming
            * `confirmed` - Confirmed
            * `completed` - Completed
            * `failed` - Failed
            * `expired` - Expired
            * `cancelled` - Cancelled
            * `refunded` - Refunded
        network (Union[None, Unset, str]): Blockchain network (mainnet, testnet, etc.)
        description (Union[Unset, str]): Payment description
        expires_at (Union[None, Unset, datetime.datetime]): Payment expiration time
    """

    id: UUID
    internal_payment_id: str
    provider_payment_id: Union[None, str]
    amount_usd: float
    currency_code: str
    actual_amount_usd: Union[None, float]
    actual_currency_code: Union[None, str]
    fee_amount_usd: Union[None, float]
    provider: UniversalPaymentProvider
    provider_display: str
    status_display: str
    pay_address: Union[None, str]
    pay_amount: Union[None, float]
    is_pending: bool
    is_completed: bool
    is_failed: bool
    completed_at: Union[None, datetime.datetime]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    order_id: Union[None, Unset, str] = UNSET
    status: Union[Unset, UniversalPaymentStatus] = UNSET
    network: Union[None, Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    expires_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        internal_payment_id = self.internal_payment_id

        provider_payment_id: Union[None, str]
        provider_payment_id = self.provider_payment_id

        amount_usd = self.amount_usd

        currency_code = self.currency_code

        actual_amount_usd: Union[None, float]
        actual_amount_usd = self.actual_amount_usd

        actual_currency_code: Union[None, str]
        actual_currency_code = self.actual_currency_code

        fee_amount_usd: Union[None, float]
        fee_amount_usd = self.fee_amount_usd

        provider: str = self.provider

        provider_display = self.provider_display

        status_display = self.status_display

        pay_address: Union[None, str]
        pay_address = self.pay_address

        pay_amount: Union[None, float]
        pay_amount = self.pay_amount

        is_pending = self.is_pending

        is_completed = self.is_completed

        is_failed = self.is_failed

        completed_at: Union[None, str]
        if isinstance(self.completed_at, datetime.datetime):
            completed_at = self.completed_at.isoformat()
        else:
            completed_at = self.completed_at

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        order_id: Union[None, Unset, str]
        if isinstance(self.order_id, Unset):
            order_id = UNSET
        else:
            order_id = self.order_id

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status

        network: Union[None, Unset, str]
        if isinstance(self.network, Unset):
            network = UNSET
        else:
            network = self.network

        description = self.description

        expires_at: Union[None, Unset, str]
        if isinstance(self.expires_at, Unset):
            expires_at = UNSET
        elif isinstance(self.expires_at, datetime.datetime):
            expires_at = self.expires_at.isoformat()
        else:
            expires_at = self.expires_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "internal_payment_id": internal_payment_id,
                "provider_payment_id": provider_payment_id,
                "amount_usd": amount_usd,
                "currency_code": currency_code,
                "actual_amount_usd": actual_amount_usd,
                "actual_currency_code": actual_currency_code,
                "fee_amount_usd": fee_amount_usd,
                "provider": provider,
                "provider_display": provider_display,
                "status_display": status_display,
                "pay_address": pay_address,
                "pay_amount": pay_amount,
                "is_pending": is_pending,
                "is_completed": is_completed,
                "is_failed": is_failed,
                "completed_at": completed_at,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if order_id is not UNSET:
            field_dict["order_id"] = order_id
        if status is not UNSET:
            field_dict["status"] = status
        if network is not UNSET:
            field_dict["network"] = network
        if description is not UNSET:
            field_dict["description"] = description
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        internal_payment_id = d.pop("internal_payment_id")

        def _parse_provider_payment_id(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        provider_payment_id = _parse_provider_payment_id(d.pop("provider_payment_id"))

        amount_usd = d.pop("amount_usd")

        currency_code = d.pop("currency_code")

        def _parse_actual_amount_usd(data: object) -> Union[None, float]:
            if data is None:
                return data
            return cast(Union[None, float], data)

        actual_amount_usd = _parse_actual_amount_usd(d.pop("actual_amount_usd"))

        def _parse_actual_currency_code(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        actual_currency_code = _parse_actual_currency_code(d.pop("actual_currency_code"))

        def _parse_fee_amount_usd(data: object) -> Union[None, float]:
            if data is None:
                return data
            return cast(Union[None, float], data)

        fee_amount_usd = _parse_fee_amount_usd(d.pop("fee_amount_usd"))

        provider = check_universal_payment_provider(d.pop("provider"))

        provider_display = d.pop("provider_display")

        status_display = d.pop("status_display")

        def _parse_pay_address(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        pay_address = _parse_pay_address(d.pop("pay_address"))

        def _parse_pay_amount(data: object) -> Union[None, float]:
            if data is None:
                return data
            return cast(Union[None, float], data)

        pay_amount = _parse_pay_amount(d.pop("pay_amount"))

        is_pending = d.pop("is_pending")

        is_completed = d.pop("is_completed")

        is_failed = d.pop("is_failed")

        def _parse_completed_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                completed_at_type_0 = isoparse(data)

                return completed_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        completed_at = _parse_completed_at(d.pop("completed_at"))

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        def _parse_order_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        order_id = _parse_order_id(d.pop("order_id", UNSET))

        _status = d.pop("status", UNSET)
        status: Union[Unset, UniversalPaymentStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = check_universal_payment_status(_status)

        def _parse_network(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        network = _parse_network(d.pop("network", UNSET))

        description = d.pop("description", UNSET)

        def _parse_expires_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expires_at_type_0 = isoparse(data)

                return expires_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        expires_at = _parse_expires_at(d.pop("expires_at", UNSET))

        universal_payment = cls(
            id=id,
            internal_payment_id=internal_payment_id,
            provider_payment_id=provider_payment_id,
            amount_usd=amount_usd,
            currency_code=currency_code,
            actual_amount_usd=actual_amount_usd,
            actual_currency_code=actual_currency_code,
            fee_amount_usd=fee_amount_usd,
            provider=provider,
            provider_display=provider_display,
            status_display=status_display,
            pay_address=pay_address,
            pay_amount=pay_amount,
            is_pending=is_pending,
            is_completed=is_completed,
            is_failed=is_failed,
            completed_at=completed_at,
            created_at=created_at,
            updated_at=updated_at,
            order_id=order_id,
            status=status,
            network=network,
            description=description,
            expires_at=expires_at,
        )

        universal_payment.additional_properties = d
        return universal_payment

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
