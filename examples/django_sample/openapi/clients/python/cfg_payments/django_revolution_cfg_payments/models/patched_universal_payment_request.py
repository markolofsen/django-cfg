from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field
import json
from .. import types

from ..types import UNSET, Unset

from ..models.patched_universal_payment_request_provider import check_patched_universal_payment_request_provider
from ..models.patched_universal_payment_request_provider import PatchedUniversalPaymentRequestProvider
from ..models.patched_universal_payment_request_status import check_patched_universal_payment_request_status
from ..models.patched_universal_payment_request_status import PatchedUniversalPaymentRequestStatus
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
import datetime


T = TypeVar("T", bound="PatchedUniversalPaymentRequest")


@_attrs_define
class PatchedUniversalPaymentRequest:
    """Universal payment with status info.

    Attributes:
        order_id (Union[None, Unset, str]): Order reference ID
        amount_usd (Union[Unset, float]): Payment amount in USD
        currency_code (Union[Unset, str]): Currency used for payment
        provider (Union[Unset, PatchedUniversalPaymentRequestProvider]): Payment provider

            * `nowpayments` - NowPayments
            * `stripe` - Stripe
            * `internal` - Internal
        status (Union[Unset, PatchedUniversalPaymentRequestStatus]): Payment status

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

    order_id: Union[None, Unset, str] = UNSET
    amount_usd: Union[Unset, float] = UNSET
    currency_code: Union[Unset, str] = UNSET
    provider: Union[Unset, PatchedUniversalPaymentRequestProvider] = UNSET
    status: Union[Unset, PatchedUniversalPaymentRequestStatus] = UNSET
    network: Union[None, Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    expires_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        order_id: Union[None, Unset, str]
        if isinstance(self.order_id, Unset):
            order_id = UNSET
        else:
            order_id = self.order_id

        amount_usd = self.amount_usd

        currency_code = self.currency_code

        provider: Union[Unset, str] = UNSET
        if not isinstance(self.provider, Unset):
            provider = self.provider

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
        field_dict.update({})
        if order_id is not UNSET:
            field_dict["order_id"] = order_id
        if amount_usd is not UNSET:
            field_dict["amount_usd"] = amount_usd
        if currency_code is not UNSET:
            field_dict["currency_code"] = currency_code
        if provider is not UNSET:
            field_dict["provider"] = provider
        if status is not UNSET:
            field_dict["status"] = status
        if network is not UNSET:
            field_dict["network"] = network
        if description is not UNSET:
            field_dict["description"] = description
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        if not isinstance(self.order_id, Unset):
            if isinstance(self.order_id, str):
                files.append(("order_id", (None, str(self.order_id).encode(), "text/plain")))
            else:
                files.append(("order_id", (None, str(self.order_id).encode(), "text/plain")))

        if not isinstance(self.amount_usd, Unset):
            files.append(("amount_usd", (None, str(self.amount_usd).encode(), "text/plain")))

        if not isinstance(self.currency_code, Unset):
            files.append(("currency_code", (None, str(self.currency_code).encode(), "text/plain")))

        if not isinstance(self.provider, Unset):
            files.append(("provider", (None, str(self.provider).encode(), "text/plain")))

        if not isinstance(self.status, Unset):
            files.append(("status", (None, str(self.status).encode(), "text/plain")))

        if not isinstance(self.network, Unset):
            if isinstance(self.network, str):
                files.append(("network", (None, str(self.network).encode(), "text/plain")))
            else:
                files.append(("network", (None, str(self.network).encode(), "text/plain")))

        if not isinstance(self.description, Unset):
            files.append(("description", (None, str(self.description).encode(), "text/plain")))

        if not isinstance(self.expires_at, Unset):
            if isinstance(self.expires_at, datetime.datetime):
                files.append(("expires_at", (None, self.expires_at.isoformat().encode(), "text/plain")))
            else:
                files.append(("expires_at", (None, str(self.expires_at).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_order_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        order_id = _parse_order_id(d.pop("order_id", UNSET))

        amount_usd = d.pop("amount_usd", UNSET)

        currency_code = d.pop("currency_code", UNSET)

        _provider = d.pop("provider", UNSET)
        provider: Union[Unset, PatchedUniversalPaymentRequestProvider]
        if isinstance(_provider, Unset):
            provider = UNSET
        else:
            provider = check_patched_universal_payment_request_provider(_provider)

        _status = d.pop("status", UNSET)
        status: Union[Unset, PatchedUniversalPaymentRequestStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = check_patched_universal_payment_request_status(_status)

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

        patched_universal_payment_request = cls(
            order_id=order_id,
            amount_usd=amount_usd,
            currency_code=currency_code,
            provider=provider,
            status=status,
            network=network,
            description=description,
            expires_at=expires_at,
        )

        patched_universal_payment_request.additional_properties = d
        return patched_universal_payment_request

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
