from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union


T = TypeVar("T", bound="TariffList")


@_attrs_define
class TariffList:
    """Simplified tariff for lists.

    Attributes:
        id (int):
        name (str): Tariff name
        display_name (str): Human-readable tariff name
        is_free (str):
        monthly_price (Union[Unset, float]): Monthly price in USD
        is_active (Union[Unset, bool]): Is this tariff active
    """

    id: int
    name: str
    display_name: str
    is_free: str
    monthly_price: Union[Unset, float] = UNSET
    is_active: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        display_name = self.display_name

        is_free = self.is_free

        monthly_price = self.monthly_price

        is_active = self.is_active

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "display_name": display_name,
                "is_free": is_free,
            }
        )
        if monthly_price is not UNSET:
            field_dict["monthly_price"] = monthly_price
        if is_active is not UNSET:
            field_dict["is_active"] = is_active

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        display_name = d.pop("display_name")

        is_free = d.pop("is_free")

        monthly_price = d.pop("monthly_price", UNSET)

        is_active = d.pop("is_active", UNSET)

        tariff_list = cls(
            id=id,
            name=name,
            display_name=display_name,
            is_free=is_free,
            monthly_price=monthly_price,
            is_active=is_active,
        )

        tariff_list.additional_properties = d
        return tariff_list

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
