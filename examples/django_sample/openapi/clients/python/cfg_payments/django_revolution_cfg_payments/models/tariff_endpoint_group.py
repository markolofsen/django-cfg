from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union


T = TypeVar("T", bound="TariffEndpointGroup")


@_attrs_define
class TariffEndpointGroup:
    """Tariff endpoint group association.

    Attributes:
        id (int):
        tariff (int): Tariff plan
        tariff_name (str):
        endpoint_group (int): Endpoint group
        endpoint_group_name (str):
        is_enabled (Union[Unset, bool]): Is this endpoint group enabled for this tariff
    """

    id: int
    tariff: int
    tariff_name: str
    endpoint_group: int
    endpoint_group_name: str
    is_enabled: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        tariff = self.tariff

        tariff_name = self.tariff_name

        endpoint_group = self.endpoint_group

        endpoint_group_name = self.endpoint_group_name

        is_enabled = self.is_enabled

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "tariff": tariff,
                "tariff_name": tariff_name,
                "endpoint_group": endpoint_group,
                "endpoint_group_name": endpoint_group_name,
            }
        )
        if is_enabled is not UNSET:
            field_dict["is_enabled"] = is_enabled

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        tariff = d.pop("tariff")

        tariff_name = d.pop("tariff_name")

        endpoint_group = d.pop("endpoint_group")

        endpoint_group_name = d.pop("endpoint_group_name")

        is_enabled = d.pop("is_enabled", UNSET)

        tariff_endpoint_group = cls(
            id=id,
            tariff=tariff,
            tariff_name=tariff_name,
            endpoint_group=endpoint_group,
            endpoint_group_name=endpoint_group_name,
            is_enabled=is_enabled,
        )

        tariff_endpoint_group.additional_properties = d
        return tariff_endpoint_group

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
