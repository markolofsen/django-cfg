from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.subscription_create_tier import check_subscription_create_tier
from ..models.subscription_create_tier import SubscriptionCreateTier
from typing import cast


T = TypeVar("T", bound="SubscriptionCreate")


@_attrs_define
class SubscriptionCreate:
    """Create subscription request.

    Attributes:
        endpoint_group_id (int):
        tier (SubscriptionCreateTier): * `basic` - Basic
            * `premium` - Premium
            * `enterprise` - Enterprise
    """

    endpoint_group_id: int
    tier: SubscriptionCreateTier
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        endpoint_group_id = self.endpoint_group_id

        tier: str = self.tier

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "endpoint_group_id": endpoint_group_id,
                "tier": tier,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        endpoint_group_id = d.pop("endpoint_group_id")

        tier = check_subscription_create_tier(d.pop("tier"))

        subscription_create = cls(
            endpoint_group_id=endpoint_group_id,
            tier=tier,
        )

        subscription_create.additional_properties = d
        return subscription_create

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
