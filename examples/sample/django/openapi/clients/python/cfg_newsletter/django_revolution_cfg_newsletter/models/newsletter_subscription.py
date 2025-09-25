from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
import datetime


T = TypeVar("T", bound="NewsletterSubscription")


@_attrs_define
class NewsletterSubscription:
    """Serializer for NewsletterSubscription model.

    Attributes:
        id (int):
        newsletter (int):
        newsletter_title (str):
        user_email (str):
        email (str):
        subscribed_at (datetime.datetime):
        unsubscribed_at (Union[None, datetime.datetime]):
        user (Union[None, Unset, int]):
        is_active (Union[Unset, bool]):
    """

    id: int
    newsletter: int
    newsletter_title: str
    user_email: str
    email: str
    subscribed_at: datetime.datetime
    unsubscribed_at: Union[None, datetime.datetime]
    user: Union[None, Unset, int] = UNSET
    is_active: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        newsletter = self.newsletter

        newsletter_title = self.newsletter_title

        user_email = self.user_email

        email = self.email

        subscribed_at = self.subscribed_at.isoformat()

        unsubscribed_at: Union[None, str]
        if isinstance(self.unsubscribed_at, datetime.datetime):
            unsubscribed_at = self.unsubscribed_at.isoformat()
        else:
            unsubscribed_at = self.unsubscribed_at

        user: Union[None, Unset, int]
        if isinstance(self.user, Unset):
            user = UNSET
        else:
            user = self.user

        is_active = self.is_active

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "newsletter": newsletter,
                "newsletter_title": newsletter_title,
                "user_email": user_email,
                "email": email,
                "subscribed_at": subscribed_at,
                "unsubscribed_at": unsubscribed_at,
            }
        )
        if user is not UNSET:
            field_dict["user"] = user
        if is_active is not UNSET:
            field_dict["is_active"] = is_active

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        newsletter = d.pop("newsletter")

        newsletter_title = d.pop("newsletter_title")

        user_email = d.pop("user_email")

        email = d.pop("email")

        subscribed_at = isoparse(d.pop("subscribed_at"))

        def _parse_unsubscribed_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                unsubscribed_at_type_0 = isoparse(data)

                return unsubscribed_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        unsubscribed_at = _parse_unsubscribed_at(d.pop("unsubscribed_at"))

        def _parse_user(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        user = _parse_user(d.pop("user", UNSET))

        is_active = d.pop("is_active", UNSET)

        newsletter_subscription = cls(
            id=id,
            newsletter=newsletter,
            newsletter_title=newsletter_title,
            user_email=user_email,
            email=email,
            subscribed_at=subscribed_at,
            unsubscribed_at=unsubscribed_at,
            user=user,
            is_active=is_active,
        )

        newsletter_subscription.additional_properties = d
        return newsletter_subscription

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
