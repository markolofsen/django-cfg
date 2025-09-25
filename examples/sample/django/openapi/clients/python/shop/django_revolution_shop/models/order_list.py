from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.order_list_status import check_order_list_status
from ..models.order_list_status import OrderListStatus
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import Union
import datetime


T = TypeVar("T", bound="OrderList")


@_attrs_define
class OrderList:
    """Serializer for order list view.

    Attributes:
        id (int):
        order_number (str):
        customer (str):
        items_count (str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        status (Union[Unset, OrderListStatus]): * `pending` - Pending
            * `processing` - Processing
            * `shipped` - Shipped
            * `delivered` - Delivered
            * `cancelled` - Cancelled
            * `refunded` - Refunded
        subtotal (Union[Unset, str]):
        total_amount (Union[Unset, str]):
    """

    id: int
    order_number: str
    customer: str
    items_count: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    status: Union[Unset, OrderListStatus] = UNSET
    subtotal: Union[Unset, str] = UNSET
    total_amount: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        order_number = self.order_number

        customer = self.customer

        items_count = self.items_count

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status

        subtotal = self.subtotal

        total_amount = self.total_amount

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "order_number": order_number,
                "customer": customer,
                "items_count": items_count,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if status is not UNSET:
            field_dict["status"] = status
        if subtotal is not UNSET:
            field_dict["subtotal"] = subtotal
        if total_amount is not UNSET:
            field_dict["total_amount"] = total_amount

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        order_number = d.pop("order_number")

        customer = d.pop("customer")

        items_count = d.pop("items_count")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        _status = d.pop("status", UNSET)
        status: Union[Unset, OrderListStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = check_order_list_status(_status)

        subtotal = d.pop("subtotal", UNSET)

        total_amount = d.pop("total_amount", UNSET)

        order_list = cls(
            id=id,
            order_number=order_number,
            customer=customer,
            items_count=items_count,
            created_at=created_at,
            updated_at=updated_at,
            status=status,
            subtotal=subtotal,
            total_amount=total_amount,
        )

        order_list.additional_properties = d
        return order_list

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
