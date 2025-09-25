from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field
import json
from .. import types

from ..types import UNSET, Unset

from ..models.subscription_create_request_tier import check_subscription_create_request_tier
from ..models.subscription_create_request_tier import SubscriptionCreateRequestTier
from typing import cast


T = TypeVar("T", bound="SubscriptionCreateRequest")


@_attrs_define
class SubscriptionCreateRequest:
    """Create subscription request.

    Attributes:
        endpoint_group_id (int):
        tier (SubscriptionCreateRequestTier): * `basic` - Basic
            * `premium` - Premium
            * `enterprise` - Enterprise
    """

    endpoint_group_id: int
    tier: SubscriptionCreateRequestTier
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

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        files.append(("endpoint_group_id", (None, str(self.endpoint_group_id).encode(), "text/plain")))

        files.append(("tier", (None, str(self.tier).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        endpoint_group_id = d.pop("endpoint_group_id")

        tier = check_subscription_create_request_tier(d.pop("tier"))

        subscription_create_request = cls(
            endpoint_group_id=endpoint_group_id,
            tier=tier,
        )

        subscription_create_request.additional_properties = d
        return subscription_create_request

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
