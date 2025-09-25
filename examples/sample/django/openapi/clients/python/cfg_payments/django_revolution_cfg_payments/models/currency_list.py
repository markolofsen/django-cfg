from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.currency_list_currency_type import check_currency_list_currency_type
from ..models.currency_list_currency_type import CurrencyListCurrencyType
from ..types import UNSET, Unset
from typing import cast
from typing import Union


T = TypeVar("T", bound="CurrencyList")


@_attrs_define
class CurrencyList:
    """Simplified currency for lists.

    Attributes:
        id (int):
        code (str): Currency code (e.g., USD, BTC, ETH)
        name (str): Full currency name
        currency_type (CurrencyListCurrencyType): Type of currency

            * `fiat` - Fiat Currency
            * `crypto` - Cryptocurrency
        currency_type_display (str):
        is_active (Union[Unset, bool]): Whether this currency is active for payments
    """

    id: int
    code: str
    name: str
    currency_type: CurrencyListCurrencyType
    currency_type_display: str
    is_active: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        code = self.code

        name = self.name

        currency_type: str = self.currency_type

        currency_type_display = self.currency_type_display

        is_active = self.is_active

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "code": code,
                "name": name,
                "currency_type": currency_type,
                "currency_type_display": currency_type_display,
            }
        )
        if is_active is not UNSET:
            field_dict["is_active"] = is_active

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        code = d.pop("code")

        name = d.pop("name")

        currency_type = check_currency_list_currency_type(d.pop("currency_type"))

        currency_type_display = d.pop("currency_type_display")

        is_active = d.pop("is_active", UNSET)

        currency_list = cls(
            id=id,
            code=code,
            name=name,
            currency_type=currency_type,
            currency_type_display=currency_type_display,
            is_active=is_active,
        )

        currency_list.additional_properties = d
        return currency_list

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
