from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union


T = TypeVar("T", bound="CurrencyNetwork")


@_attrs_define
class CurrencyNetwork:
    """Currency network with status.

    Attributes:
        id (int):
        currency (int): Currency this network supports
        currency_code (str):
        currency_name (str):
        network_code (str): Network code for API integration
        network_name (str): Network name (e.g., mainnet, polygon, bsc)
        is_active (Union[Unset, bool]): Whether this network is active
        confirmation_blocks (Union[Unset, int]): Number of confirmations required
    """

    id: int
    currency: int
    currency_code: str
    currency_name: str
    network_code: str
    network_name: str
    is_active: Union[Unset, bool] = UNSET
    confirmation_blocks: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        currency = self.currency

        currency_code = self.currency_code

        currency_name = self.currency_name

        network_code = self.network_code

        network_name = self.network_name

        is_active = self.is_active

        confirmation_blocks = self.confirmation_blocks

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "currency": currency,
                "currency_code": currency_code,
                "currency_name": currency_name,
                "network_code": network_code,
                "network_name": network_name,
            }
        )
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if confirmation_blocks is not UNSET:
            field_dict["confirmation_blocks"] = confirmation_blocks

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        currency = d.pop("currency")

        currency_code = d.pop("currency_code")

        currency_name = d.pop("currency_name")

        network_code = d.pop("network_code")

        network_name = d.pop("network_name")

        is_active = d.pop("is_active", UNSET)

        confirmation_blocks = d.pop("confirmation_blocks", UNSET)

        currency_network = cls(
            id=id,
            currency=currency,
            currency_code=currency_code,
            currency_name=currency_name,
            network_code=network_code,
            network_name=network_name,
            is_active=is_active,
            confirmation_blocks=confirmation_blocks,
        )

        currency_network.additional_properties = d
        return currency_network

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
