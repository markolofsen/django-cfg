from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.order_detail_status import check_order_detail_status
from ..models.order_detail_status import OrderDetailStatus
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
import datetime

if TYPE_CHECKING:
    from ..models.order_item import OrderItem


T = TypeVar("T", bound="OrderDetail")


@_attrs_define
class OrderDetail:
    """Serializer for order detail view.

    Attributes:
        id (int):
        order_number (str):
        customer (str):
        billing_address (str):
        shipping_address (str):
        items (list['OrderItem']):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        status (Union[Unset, OrderDetailStatus]): * `pending` - Pending
            * `processing` - Processing
            * `shipped` - Shipped
            * `delivered` - Delivered
            * `cancelled` - Cancelled
            * `refunded` - Refunded
        subtotal (Union[Unset, str]):
        tax_amount (Union[Unset, str]):
        shipping_amount (Union[Unset, str]):
        discount_amount (Union[Unset, str]):
        total_amount (Union[Unset, str]):
        customer_notes (Union[Unset, str]):
        admin_notes (Union[Unset, str]):
        shipped_at (Union[None, Unset, datetime.datetime]):
        delivered_at (Union[None, Unset, datetime.datetime]):
    """

    id: int
    order_number: str
    customer: str
    billing_address: str
    shipping_address: str
    items: list["OrderItem"]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    status: Union[Unset, OrderDetailStatus] = UNSET
    subtotal: Union[Unset, str] = UNSET
    tax_amount: Union[Unset, str] = UNSET
    shipping_amount: Union[Unset, str] = UNSET
    discount_amount: Union[Unset, str] = UNSET
    total_amount: Union[Unset, str] = UNSET
    customer_notes: Union[Unset, str] = UNSET
    admin_notes: Union[Unset, str] = UNSET
    shipped_at: Union[None, Unset, datetime.datetime] = UNSET
    delivered_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.order_item import OrderItem

        id = self.id

        order_number = self.order_number

        customer = self.customer

        billing_address = self.billing_address

        shipping_address = self.shipping_address

        items = []
        for items_item_data in self.items:
            items_item = items_item_data.to_dict()
            items.append(items_item)

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status

        subtotal = self.subtotal

        tax_amount = self.tax_amount

        shipping_amount = self.shipping_amount

        discount_amount = self.discount_amount

        total_amount = self.total_amount

        customer_notes = self.customer_notes

        admin_notes = self.admin_notes

        shipped_at: Union[None, Unset, str]
        if isinstance(self.shipped_at, Unset):
            shipped_at = UNSET
        elif isinstance(self.shipped_at, datetime.datetime):
            shipped_at = self.shipped_at.isoformat()
        else:
            shipped_at = self.shipped_at

        delivered_at: Union[None, Unset, str]
        if isinstance(self.delivered_at, Unset):
            delivered_at = UNSET
        elif isinstance(self.delivered_at, datetime.datetime):
            delivered_at = self.delivered_at.isoformat()
        else:
            delivered_at = self.delivered_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "order_number": order_number,
                "customer": customer,
                "billing_address": billing_address,
                "shipping_address": shipping_address,
                "items": items,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if status is not UNSET:
            field_dict["status"] = status
        if subtotal is not UNSET:
            field_dict["subtotal"] = subtotal
        if tax_amount is not UNSET:
            field_dict["tax_amount"] = tax_amount
        if shipping_amount is not UNSET:
            field_dict["shipping_amount"] = shipping_amount
        if discount_amount is not UNSET:
            field_dict["discount_amount"] = discount_amount
        if total_amount is not UNSET:
            field_dict["total_amount"] = total_amount
        if customer_notes is not UNSET:
            field_dict["customer_notes"] = customer_notes
        if admin_notes is not UNSET:
            field_dict["admin_notes"] = admin_notes
        if shipped_at is not UNSET:
            field_dict["shipped_at"] = shipped_at
        if delivered_at is not UNSET:
            field_dict["delivered_at"] = delivered_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.order_item import OrderItem

        d = dict(src_dict)
        id = d.pop("id")

        order_number = d.pop("order_number")

        customer = d.pop("customer")

        billing_address = d.pop("billing_address")

        shipping_address = d.pop("shipping_address")

        items = []
        _items = d.pop("items")
        for items_item_data in _items:
            items_item = OrderItem.from_dict(items_item_data)

            items.append(items_item)

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        _status = d.pop("status", UNSET)
        status: Union[Unset, OrderDetailStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = check_order_detail_status(_status)

        subtotal = d.pop("subtotal", UNSET)

        tax_amount = d.pop("tax_amount", UNSET)

        shipping_amount = d.pop("shipping_amount", UNSET)

        discount_amount = d.pop("discount_amount", UNSET)

        total_amount = d.pop("total_amount", UNSET)

        customer_notes = d.pop("customer_notes", UNSET)

        admin_notes = d.pop("admin_notes", UNSET)

        def _parse_shipped_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                shipped_at_type_0 = isoparse(data)

                return shipped_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        shipped_at = _parse_shipped_at(d.pop("shipped_at", UNSET))

        def _parse_delivered_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                delivered_at_type_0 = isoparse(data)

                return delivered_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        delivered_at = _parse_delivered_at(d.pop("delivered_at", UNSET))

        order_detail = cls(
            id=id,
            order_number=order_number,
            customer=customer,
            billing_address=billing_address,
            shipping_address=shipping_address,
            items=items,
            created_at=created_at,
            updated_at=updated_at,
            status=status,
            subtotal=subtotal,
            tax_amount=tax_amount,
            shipping_amount=shipping_amount,
            discount_amount=discount_amount,
            total_amount=total_amount,
            customer_notes=customer_notes,
            admin_notes=admin_notes,
            shipped_at=shipped_at,
            delivered_at=delivered_at,
        )

        order_detail.additional_properties = d
        return order_detail

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
