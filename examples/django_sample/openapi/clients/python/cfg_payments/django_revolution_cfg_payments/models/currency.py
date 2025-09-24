from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.currency_currency_type import check_currency_currency_type
from ..models.currency_currency_type import CurrencyCurrencyType
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
import datetime


T = TypeVar("T", bound="Currency")


@_attrs_define
class Currency:
    """Currency with type info.

    Attributes:
        id (int):
        code (str): Currency code (e.g., USD, BTC, ETH)
        name (str): Full currency name
        symbol (str): Currency symbol (e.g., $, ₿, Ξ)
        currency_type (CurrencyCurrencyType): Type of currency

            * `fiat` - Fiat Currency
            * `crypto` - Cryptocurrency
        currency_type_display (str):
        is_crypto (str):
        is_fiat (str):
        rate_updated_at (Union[None, datetime.datetime]): When the exchange rate was last updated
        decimal_places (Union[Unset, int]): Number of decimal places for this currency
        usd_rate (Union[Unset, float]): Exchange rate to USD (1 unit of this currency = X USD)
        is_active (Union[Unset, bool]): Whether this currency is active for payments
        min_payment_amount (Union[Unset, float]): Minimum payment amount for this currency
    """

    id: int
    code: str
    name: str
    symbol: str
    currency_type: CurrencyCurrencyType
    currency_type_display: str
    is_crypto: str
    is_fiat: str
    rate_updated_at: Union[None, datetime.datetime]
    decimal_places: Union[Unset, int] = UNSET
    usd_rate: Union[Unset, float] = UNSET
    is_active: Union[Unset, bool] = UNSET
    min_payment_amount: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        code = self.code

        name = self.name

        symbol = self.symbol

        currency_type: str = self.currency_type

        currency_type_display = self.currency_type_display

        is_crypto = self.is_crypto

        is_fiat = self.is_fiat

        rate_updated_at: Union[None, str]
        if isinstance(self.rate_updated_at, datetime.datetime):
            rate_updated_at = self.rate_updated_at.isoformat()
        else:
            rate_updated_at = self.rate_updated_at

        decimal_places = self.decimal_places

        usd_rate = self.usd_rate

        is_active = self.is_active

        min_payment_amount = self.min_payment_amount

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "code": code,
                "name": name,
                "symbol": symbol,
                "currency_type": currency_type,
                "currency_type_display": currency_type_display,
                "is_crypto": is_crypto,
                "is_fiat": is_fiat,
                "rate_updated_at": rate_updated_at,
            }
        )
        if decimal_places is not UNSET:
            field_dict["decimal_places"] = decimal_places
        if usd_rate is not UNSET:
            field_dict["usd_rate"] = usd_rate
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if min_payment_amount is not UNSET:
            field_dict["min_payment_amount"] = min_payment_amount

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        code = d.pop("code")

        name = d.pop("name")

        symbol = d.pop("symbol")

        currency_type = check_currency_currency_type(d.pop("currency_type"))

        currency_type_display = d.pop("currency_type_display")

        is_crypto = d.pop("is_crypto")

        is_fiat = d.pop("is_fiat")

        def _parse_rate_updated_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                rate_updated_at_type_0 = isoparse(data)

                return rate_updated_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        rate_updated_at = _parse_rate_updated_at(d.pop("rate_updated_at"))

        decimal_places = d.pop("decimal_places", UNSET)

        usd_rate = d.pop("usd_rate", UNSET)

        is_active = d.pop("is_active", UNSET)

        min_payment_amount = d.pop("min_payment_amount", UNSET)

        currency = cls(
            id=id,
            code=code,
            name=name,
            symbol=symbol,
            currency_type=currency_type,
            currency_type_display=currency_type_display,
            is_crypto=is_crypto,
            is_fiat=is_fiat,
            rate_updated_at=rate_updated_at,
            decimal_places=decimal_places,
            usd_rate=usd_rate,
            is_active=is_active,
            min_payment_amount=min_payment_amount,
        )

        currency.additional_properties = d
        return currency

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
