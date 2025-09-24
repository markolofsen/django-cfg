from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field
import json
from .. import types

from ..types import UNSET, Unset

from ..models.payment_create_request_provider import check_payment_create_request_provider
from ..models.payment_create_request_provider import PaymentCreateRequestProvider
from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union


T = TypeVar("T", bound="PaymentCreateRequest")


@_attrs_define
class PaymentCreateRequest:
    """Create payment request.

    Attributes:
        amount_usd (float): Payment amount in USD
        currency_code (str): Currency used for payment
        provider (PaymentCreateRequestProvider): Payment provider

            * `nowpayments` - NowPayments
            * `stripe` - Stripe
            * `internal` - Internal
        description (Union[Unset, str]): Payment description
        order_id (Union[None, Unset, str]): Order reference ID
    """

    amount_usd: float
    currency_code: str
    provider: PaymentCreateRequestProvider
    description: Union[Unset, str] = UNSET
    order_id: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        amount_usd = self.amount_usd

        currency_code = self.currency_code

        provider: str = self.provider

        description = self.description

        order_id: Union[None, Unset, str]
        if isinstance(self.order_id, Unset):
            order_id = UNSET
        else:
            order_id = self.order_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "amount_usd": amount_usd,
                "currency_code": currency_code,
                "provider": provider,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if order_id is not UNSET:
            field_dict["order_id"] = order_id

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        files.append(("amount_usd", (None, str(self.amount_usd).encode(), "text/plain")))

        files.append(("currency_code", (None, str(self.currency_code).encode(), "text/plain")))

        files.append(("provider", (None, str(self.provider).encode(), "text/plain")))

        if not isinstance(self.description, Unset):
            files.append(("description", (None, str(self.description).encode(), "text/plain")))

        if not isinstance(self.order_id, Unset):
            if isinstance(self.order_id, str):
                files.append(("order_id", (None, str(self.order_id).encode(), "text/plain")))
            else:
                files.append(("order_id", (None, str(self.order_id).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        amount_usd = d.pop("amount_usd")

        currency_code = d.pop("currency_code")

        provider = check_payment_create_request_provider(d.pop("provider"))

        description = d.pop("description", UNSET)

        def _parse_order_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        order_id = _parse_order_id(d.pop("order_id", UNSET))

        payment_create_request = cls(
            amount_usd=amount_usd,
            currency_code=currency_code,
            provider=provider,
            description=description,
            order_id=order_id,
        )

        payment_create_request.additional_properties = d
        return payment_create_request

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
