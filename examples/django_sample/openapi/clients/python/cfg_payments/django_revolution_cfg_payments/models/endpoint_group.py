from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union


T = TypeVar("T", bound="EndpointGroup")


@_attrs_define
class EndpointGroup:
    """Endpoint group with pricing tiers.

    Attributes:
        id (int):
        name (str): Endpoint group name
        display_name (str): Human-readable name
        description (Union[Unset, str]): Group description
        basic_price (Union[Unset, float]): Basic tier monthly price
        premium_price (Union[Unset, float]): Premium tier monthly price
        enterprise_price (Union[Unset, float]): Enterprise tier monthly price
        basic_limit (Union[Unset, int]): Basic tier monthly usage limit
        premium_limit (Union[Unset, int]): Premium tier monthly usage limit
        enterprise_limit (Union[Unset, int]): Enterprise tier monthly usage limit (0 = unlimited)
        is_active (Union[Unset, bool]): Is this endpoint group active
        require_api_key (Union[Unset, bool]): Require API key for access
    """

    id: int
    name: str
    display_name: str
    description: Union[Unset, str] = UNSET
    basic_price: Union[Unset, float] = UNSET
    premium_price: Union[Unset, float] = UNSET
    enterprise_price: Union[Unset, float] = UNSET
    basic_limit: Union[Unset, int] = UNSET
    premium_limit: Union[Unset, int] = UNSET
    enterprise_limit: Union[Unset, int] = UNSET
    is_active: Union[Unset, bool] = UNSET
    require_api_key: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        display_name = self.display_name

        description = self.description

        basic_price = self.basic_price

        premium_price = self.premium_price

        enterprise_price = self.enterprise_price

        basic_limit = self.basic_limit

        premium_limit = self.premium_limit

        enterprise_limit = self.enterprise_limit

        is_active = self.is_active

        require_api_key = self.require_api_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "display_name": display_name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if basic_price is not UNSET:
            field_dict["basic_price"] = basic_price
        if premium_price is not UNSET:
            field_dict["premium_price"] = premium_price
        if enterprise_price is not UNSET:
            field_dict["enterprise_price"] = enterprise_price
        if basic_limit is not UNSET:
            field_dict["basic_limit"] = basic_limit
        if premium_limit is not UNSET:
            field_dict["premium_limit"] = premium_limit
        if enterprise_limit is not UNSET:
            field_dict["enterprise_limit"] = enterprise_limit
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if require_api_key is not UNSET:
            field_dict["require_api_key"] = require_api_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        display_name = d.pop("display_name")

        description = d.pop("description", UNSET)

        basic_price = d.pop("basic_price", UNSET)

        premium_price = d.pop("premium_price", UNSET)

        enterprise_price = d.pop("enterprise_price", UNSET)

        basic_limit = d.pop("basic_limit", UNSET)

        premium_limit = d.pop("premium_limit", UNSET)

        enterprise_limit = d.pop("enterprise_limit", UNSET)

        is_active = d.pop("is_active", UNSET)

        require_api_key = d.pop("require_api_key", UNSET)

        endpoint_group = cls(
            id=id,
            name=name,
            display_name=display_name,
            description=description,
            basic_price=basic_price,
            premium_price=premium_price,
            enterprise_price=enterprise_price,
            basic_limit=basic_limit,
            premium_limit=premium_limit,
            enterprise_limit=enterprise_limit,
            is_active=is_active,
            require_api_key=require_api_key,
        )

        endpoint_group.additional_properties = d
        return endpoint_group

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
