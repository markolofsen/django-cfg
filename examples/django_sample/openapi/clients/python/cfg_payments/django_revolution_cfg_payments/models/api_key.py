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
from uuid import UUID
import datetime


T = TypeVar("T", bound="APIKey")


@_attrs_define
class APIKey:
    """API key with usage stats.

    Attributes:
        id (UUID): Unique identifier
        name (str): Human-readable key name
        key_value (str): API key value (plain text)
        key_prefix (str): Key prefix for identification
        usage_count (int): Total usage count
        is_valid (str):
        last_used (Union[None, datetime.datetime]): Last usage timestamp
        created_at (datetime.datetime):
        is_active (Union[Unset, bool]): Is key active
        expires_at (Union[None, Unset, datetime.datetime]): Key expiration
    """

    id: UUID
    name: str
    key_value: str
    key_prefix: str
    usage_count: int
    is_valid: str
    last_used: Union[None, datetime.datetime]
    created_at: datetime.datetime
    is_active: Union[Unset, bool] = UNSET
    expires_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        key_value = self.key_value

        key_prefix = self.key_prefix

        usage_count = self.usage_count

        is_valid = self.is_valid

        last_used: Union[None, str]
        if isinstance(self.last_used, datetime.datetime):
            last_used = self.last_used.isoformat()
        else:
            last_used = self.last_used

        created_at = self.created_at.isoformat()

        is_active = self.is_active

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
                "name": name,
                "key_value": key_value,
                "key_prefix": key_prefix,
                "usage_count": usage_count,
                "is_valid": is_valid,
                "last_used": last_used,
                "created_at": created_at,
            }
        )
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        key_value = d.pop("key_value")

        key_prefix = d.pop("key_prefix")

        usage_count = d.pop("usage_count")

        is_valid = d.pop("is_valid")

        def _parse_last_used(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_used_type_0 = isoparse(data)

                return last_used_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        last_used = _parse_last_used(d.pop("last_used"))

        created_at = isoparse(d.pop("created_at"))

        is_active = d.pop("is_active", UNSET)

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

        api_key = cls(
            id=id,
            name=name,
            key_value=key_value,
            key_prefix=key_prefix,
            usage_count=usage_count,
            is_valid=is_valid,
            last_used=last_used,
            created_at=created_at,
            is_active=is_active,
            expires_at=expires_at,
        )

        api_key.additional_properties = d
        return api_key

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
