from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.subscription_status import check_subscription_status
from ..models.subscription_status import SubscriptionStatus
from ..models.subscription_tier import check_subscription_tier
from ..models.subscription_tier import SubscriptionTier
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
from uuid import UUID
import datetime


T = TypeVar("T", bound="Subscription")


@_attrs_define
class Subscription:
    """Subscription with computed fields.

    Attributes:
        id (UUID): Unique identifier
        endpoint_group (int): Endpoint group
        endpoint_group_name (str):
        endpoint_group_display (str):
        tier_display (str):
        status_display (str):
        monthly_price (float): Monthly subscription price
        usage_current (int): Current month usage
        is_active_subscription (bool): Check if subscription is currently active.
        is_usage_exceeded (bool): Check if usage limit is exceeded.
        last_billed (Union[None, datetime.datetime]): Last billing date
        next_billing (Union[None, datetime.datetime]): Next billing date
        created_at (datetime.datetime):
        tier (Union[Unset, SubscriptionTier]): Subscription tier

            * `basic` - Basic
            * `premium` - Premium
            * `enterprise` - Enterprise
        status (Union[Unset, SubscriptionStatus]): Subscription status

            * `active` - Active
            * `inactive` - Inactive
            * `expired` - Expired
            * `cancelled` - Cancelled
            * `suspended` - Suspended
        usage_limit (Union[Unset, int]): Monthly usage limit (0 = unlimited)
        expires_at (Union[None, Unset, datetime.datetime]): Subscription expiration
    """

    id: UUID
    endpoint_group: int
    endpoint_group_name: str
    endpoint_group_display: str
    tier_display: str
    status_display: str
    monthly_price: float
    usage_current: int
    is_active_subscription: bool
    is_usage_exceeded: bool
    last_billed: Union[None, datetime.datetime]
    next_billing: Union[None, datetime.datetime]
    created_at: datetime.datetime
    tier: Union[Unset, SubscriptionTier] = UNSET
    status: Union[Unset, SubscriptionStatus] = UNSET
    usage_limit: Union[Unset, int] = UNSET
    expires_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        endpoint_group = self.endpoint_group

        endpoint_group_name = self.endpoint_group_name

        endpoint_group_display = self.endpoint_group_display

        tier_display = self.tier_display

        status_display = self.status_display

        monthly_price = self.monthly_price

        usage_current = self.usage_current

        is_active_subscription = self.is_active_subscription

        is_usage_exceeded = self.is_usage_exceeded

        last_billed: Union[None, str]
        if isinstance(self.last_billed, datetime.datetime):
            last_billed = self.last_billed.isoformat()
        else:
            last_billed = self.last_billed

        next_billing: Union[None, str]
        if isinstance(self.next_billing, datetime.datetime):
            next_billing = self.next_billing.isoformat()
        else:
            next_billing = self.next_billing

        created_at = self.created_at.isoformat()

        tier: Union[Unset, str] = UNSET
        if not isinstance(self.tier, Unset):
            tier = self.tier

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status

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
                "endpoint_group": endpoint_group,
                "endpoint_group_name": endpoint_group_name,
                "endpoint_group_display": endpoint_group_display,
                "tier_display": tier_display,
                "status_display": status_display,
                "monthly_price": monthly_price,
                "usage_current": usage_current,
                "is_active_subscription": is_active_subscription,
                "is_usage_exceeded": is_usage_exceeded,
                "last_billed": last_billed,
                "next_billing": next_billing,
                "created_at": created_at,
            }
        )
        if tier is not UNSET:
            field_dict["tier"] = tier
        if status is not UNSET:
            field_dict["status"] = status
        if usage_limit is not UNSET:
            field_dict["usage_limit"] = usage_limit
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        endpoint_group = d.pop("endpoint_group")

        endpoint_group_name = d.pop("endpoint_group_name")

        endpoint_group_display = d.pop("endpoint_group_display")

        tier_display = d.pop("tier_display")

        status_display = d.pop("status_display")

        monthly_price = d.pop("monthly_price")

        usage_current = d.pop("usage_current")

        is_active_subscription = d.pop("is_active_subscription")

        is_usage_exceeded = d.pop("is_usage_exceeded")

        def _parse_last_billed(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_billed_type_0 = isoparse(data)

                return last_billed_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        last_billed = _parse_last_billed(d.pop("last_billed"))

        def _parse_next_billing(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                next_billing_type_0 = isoparse(data)

                return next_billing_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        next_billing = _parse_next_billing(d.pop("next_billing"))

        created_at = isoparse(d.pop("created_at"))

        _tier = d.pop("tier", UNSET)
        tier: Union[Unset, SubscriptionTier]
        if isinstance(_tier, Unset):
            tier = UNSET
        else:
            tier = check_subscription_tier(_tier)

        _status = d.pop("status", UNSET)
        status: Union[Unset, SubscriptionStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = check_subscription_status(_status)

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

        subscription = cls(
            id=id,
            endpoint_group=endpoint_group,
            endpoint_group_name=endpoint_group_name,
            endpoint_group_display=endpoint_group_display,
            tier_display=tier_display,
            status_display=status_display,
            monthly_price=monthly_price,
            usage_current=usage_current,
            is_active_subscription=is_active_subscription,
            is_usage_exceeded=is_usage_exceeded,
            last_billed=last_billed,
            next_billing=next_billing,
            created_at=created_at,
            tier=tier,
            status=status,
            usage_limit=usage_limit,
            expires_at=expires_at,
        )

        subscription.additional_properties = d
        return subscription

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
