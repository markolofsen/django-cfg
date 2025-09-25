from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import Union
import datetime

if TYPE_CHECKING:
    from ..models.product_list import ProductList


T = TypeVar("T", bound="OrderItem")


@_attrs_define
class OrderItem:
    """Serializer for order items.

    Attributes:
        id (int):
        product (ProductList): Serializer for product list view.
        unit_price (str):
        total_price (str):
        product_name (str):
        product_sku (str):
        created_at (datetime.datetime):
        quantity (Union[Unset, int]):
    """

    id: int
    product: "ProductList"
    unit_price: str
    total_price: str
    product_name: str
    product_sku: str
    created_at: datetime.datetime
    quantity: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.product_list import ProductList

        id = self.id

        product = self.product.to_dict()

        unit_price = self.unit_price

        total_price = self.total_price

        product_name = self.product_name

        product_sku = self.product_sku

        created_at = self.created_at.isoformat()

        quantity = self.quantity

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "product": product,
                "unit_price": unit_price,
                "total_price": total_price,
                "product_name": product_name,
                "product_sku": product_sku,
                "created_at": created_at,
            }
        )
        if quantity is not UNSET:
            field_dict["quantity"] = quantity

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.product_list import ProductList

        d = dict(src_dict)
        id = d.pop("id")

        product = ProductList.from_dict(d.pop("product"))

        unit_price = d.pop("unit_price")

        total_price = d.pop("total_price")

        product_name = d.pop("product_name")

        product_sku = d.pop("product_sku")

        created_at = isoparse(d.pop("created_at"))

        quantity = d.pop("quantity", UNSET)

        order_item = cls(
            id=id,
            product=product,
            unit_price=unit_price,
            total_price=total_price,
            product_name=product_name,
            product_sku=product_sku,
            created_at=created_at,
            quantity=quantity,
        )

        order_item.additional_properties = d
        return order_item

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
