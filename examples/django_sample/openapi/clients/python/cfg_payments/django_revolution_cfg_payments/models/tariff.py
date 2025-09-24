from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union


T = TypeVar("T", bound="Tariff")


@_attrs_define
class Tariff:
    """Tariff with pricing info.

    Attributes:
        id (int):
        name (str): Tariff name
        display_name (str): Human-readable tariff name
        is_free (str):
        endpoint_groups_count (str):
        description (Union[Unset, str]): Tariff description
        monthly_price (Union[Unset, float]): Monthly price in USD
        request_limit (Union[Unset, int]): Monthly request limit (0 = unlimited)
        is_active (Union[Unset, bool]): Is this tariff active
    """

    id: int
    name: str
    display_name: str
    is_free: str
    endpoint_groups_count: str
    description: Union[Unset, str] = UNSET
    monthly_price: Union[Unset, float] = UNSET
    request_limit: Union[Unset, int] = UNSET
    is_active: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        display_name = self.display_name

        is_free = self.is_free

        endpoint_groups_count = self.endpoint_groups_count

        description = self.description

        monthly_price = self.monthly_price

        request_limit = self.request_limit

        is_active = self.is_active

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "display_name": display_name,
                "is_free": is_free,
                "endpoint_groups_count": endpoint_groups_count,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if monthly_price is not UNSET:
            field_dict["monthly_price"] = monthly_price
        if request_limit is not UNSET:
            field_dict["request_limit"] = request_limit
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

        endpoint_groups_count = d.pop("endpoint_groups_count")

        description = d.pop("description", UNSET)

        monthly_price = d.pop("monthly_price", UNSET)

        request_limit = d.pop("request_limit", UNSET)

        is_active = d.pop("is_active", UNSET)

        tariff = cls(
            id=id,
            name=name,
            display_name=display_name,
            is_free=is_free,
            endpoint_groups_count=endpoint_groups_count,
            description=description,
            monthly_price=monthly_price,
            request_limit=request_limit,
            is_active=is_active,
        )

        tariff.additional_properties = d
        return tariff

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
