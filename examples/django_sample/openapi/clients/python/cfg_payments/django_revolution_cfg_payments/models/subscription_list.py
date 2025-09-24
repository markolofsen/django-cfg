from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.subscription_list_status import check_subscription_list_status
from ..models.subscription_list_status import SubscriptionListStatus
from ..models.subscription_list_tier import check_subscription_list_tier
from ..models.subscription_list_tier import SubscriptionListTier
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
from uuid import UUID
import datetime


T = TypeVar("T", bound="SubscriptionList")


@_attrs_define
class SubscriptionList:
    """Simplified subscription for lists.

    Attributes:
        id (UUID): Unique identifier
        endpoint_group_name (str):
        status_display (str):
        monthly_price (float): Monthly subscription price
        tier (Union[Unset, SubscriptionListTier]): Subscription tier

            * `basic` - Basic
            * `premium` - Premium
            * `enterprise` - Enterprise
        status (Union[Unset, SubscriptionListStatus]): Subscription status

            * `active` - Active
            * `inactive` - Inactive
            * `expired` - Expired
            * `cancelled` - Cancelled
            * `suspended` - Suspended
        usage_current (Union[Unset, int]): Current month usage
        usage_limit (Union[Unset, int]): Monthly usage limit (0 = unlimited)
        expires_at (Union[None, Unset, datetime.datetime]): Subscription expiration
    """

    id: UUID
    endpoint_group_name: str
    status_display: str
    monthly_price: float
    tier: Union[Unset, SubscriptionListTier] = UNSET
    status: Union[Unset, SubscriptionListStatus] = UNSET
    usage_current: Union[Unset, int] = UNSET
    usage_limit: Union[Unset, int] = UNSET
    expires_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        endpoint_group_name = self.endpoint_group_name

        status_display = self.status_display

        monthly_price = self.monthly_price

        tier: Union[Unset, str] = UNSET
        if not isinstance(self.tier, Unset):
            tier = self.tier

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status

        usage_current = self.usage_current

        usage_limit = self.usage_limit

        expires_at: Union[None, Unset, str]
        if isinstance(self.expires_at, Unset):
            expires_at = UNSET
        elif isinstance(self.expires_at, datetime.datetime):
            expires_at = self.expires_at.isoformat()
        else:
            expires_at = self.expires_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "endpoint_group_name": endpoint_group_name,
                "status_display": status_display,
                "monthly_price": monthly_price,
            }
        )
        if tier is not UNSET:
            field_dict["tier"] = tier
        if status is not UNSET:
            field_dict["status"] = status
        if usage_current is not UNSET:
            field_dict["usage_current"] = usage_current
        if usage_limit is not UNSET:
            field_dict["usage_limit"] = usage_limit
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        endpoint_group_name = d.pop("endpoint_group_name")

        status_display = d.pop("status_display")

        monthly_price = d.pop("monthly_price")

        _tier = d.pop("tier", UNSET)
        tier: Union[Unset, SubscriptionListTier]
        if isinstance(_tier, Unset):
            tier = UNSET
        else:
            tier = check_subscription_list_tier(_tier)

        _status = d.pop("status", UNSET)
        status: Union[Unset, SubscriptionListStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = check_subscription_list_status(_status)

        usage_current = d.pop("usage_current", UNSET)

        usage_limit = d.pop("usage_limit", UNSET)

        def _parse_expires_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expires_at_type_0 = isoparse(data)

                return expires_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        expires_at = _parse_expires_at(d.pop("expires_at", UNSET))

        subscription_list = cls(
            id=id,
            endpoint_group_name=endpoint_group_name,
            status_display=status_display,
            monthly_price=monthly_price,
            tier=tier,
            status=status,
            usage_current=usage_current,
            usage_limit=usage_limit,
            expires_at=expires_at,
        )

        subscription_list.additional_properties = d
        return subscription_list

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
