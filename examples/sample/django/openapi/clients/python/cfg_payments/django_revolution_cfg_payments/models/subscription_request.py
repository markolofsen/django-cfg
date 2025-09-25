from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field
import json
from .. import types

from ..types import UNSET, Unset

from ..models.subscription_request_status import check_subscription_request_status
from ..models.subscription_request_status import SubscriptionRequestStatus
from ..models.subscription_request_tier import check_subscription_request_tier
from ..models.subscription_request_tier import SubscriptionRequestTier
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
import datetime


T = TypeVar("T", bound="SubscriptionRequest")


@_attrs_define
class SubscriptionRequest:
    """Subscription with computed fields.

    Attributes:
        endpoint_group (int): Endpoint group
        monthly_price (float): Monthly subscription price
        tier (Union[Unset, SubscriptionRequestTier]): Subscription tier

            * `basic` - Basic
            * `premium` - Premium
            * `enterprise` - Enterprise
        status (Union[Unset, SubscriptionRequestStatus]): Subscription status

            * `active` - Active
            * `inactive` - Inactive
            * `expired` - Expired
            * `cancelled` - Cancelled
            * `suspended` - Suspended
        usage_limit (Union[Unset, int]): Monthly usage limit (0 = unlimited)
        expires_at (Union[None, Unset, datetime.datetime]): Subscription expiration
    """

    endpoint_group: int
    monthly_price: float
    tier: Union[Unset, SubscriptionRequestTier] = UNSET
    status: Union[Unset, SubscriptionRequestStatus] = UNSET
    usage_limit: Union[Unset, int] = UNSET
    expires_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        endpoint_group = self.endpoint_group

        monthly_price = self.monthly_price

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
                "endpoint_group": endpoint_group,
                "monthly_price": monthly_price,
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

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        files.append(("endpoint_group", (None, str(self.endpoint_group).encode(), "text/plain")))

        files.append(("monthly_price", (None, str(self.monthly_price).encode(), "text/plain")))

        if not isinstance(self.tier, Unset):
            files.append(("tier", (None, str(self.tier).encode(), "text/plain")))

        if not isinstance(self.status, Unset):
            files.append(("status", (None, str(self.status).encode(), "text/plain")))

        if not isinstance(self.usage_limit, Unset):
            files.append(("usage_limit", (None, str(self.usage_limit).encode(), "text/plain")))

        if not isinstance(self.expires_at, Unset):
            if isinstance(self.expires_at, datetime.datetime):
                files.append(("expires_at", (None, self.expires_at.isoformat().encode(), "text/plain")))
            else:
                files.append(("expires_at", (None, str(self.expires_at).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        endpoint_group = d.pop("endpoint_group")

        monthly_price = d.pop("monthly_price")

        _tier = d.pop("tier", UNSET)
        tier: Union[Unset, SubscriptionRequestTier]
        if isinstance(_tier, Unset):
            tier = UNSET
        else:
            tier = check_subscription_request_tier(_tier)

        _status = d.pop("status", UNSET)
        status: Union[Unset, SubscriptionRequestStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = check_subscription_request_status(_status)

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

        subscription_request = cls(
            endpoint_group=endpoint_group,
            monthly_price=monthly_price,
            tier=tier,
            status=status,
            usage_limit=usage_limit,
            expires_at=expires_at,
        )

        subscription_request.additional_properties = d
        return subscription_request

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
