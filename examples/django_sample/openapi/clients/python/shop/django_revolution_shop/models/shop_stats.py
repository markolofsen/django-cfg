from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
    from ..models.order_list import OrderList
    from ..models.product_list import ProductList


T = TypeVar("T", bound="ShopStats")


@_attrs_define
class ShopStats:
    """Serializer for shop statistics.

    Attributes:
        total_products (int):
        active_products (int):
        out_of_stock_products (int):
        total_orders (int):
        pending_orders (int):
        total_revenue (str):
        popular_products (list['ProductList']):
        recent_orders (list['OrderList']):
    """

    total_products: int
    active_products: int
    out_of_stock_products: int
    total_orders: int
    pending_orders: int
    total_revenue: str
    popular_products: list["ProductList"]
    recent_orders: list["OrderList"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.order_list import OrderList
        from ..models.product_list import ProductList

        total_products = self.total_products

        active_products = self.active_products

        out_of_stock_products = self.out_of_stock_products

        total_orders = self.total_orders

        pending_orders = self.pending_orders

        total_revenue = self.total_revenue

        popular_products = []
        for popular_products_item_data in self.popular_products:
            popular_products_item = popular_products_item_data.to_dict()
            popular_products.append(popular_products_item)

        recent_orders = []
        for recent_orders_item_data in self.recent_orders:
            recent_orders_item = recent_orders_item_data.to_dict()
            recent_orders.append(recent_orders_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total_products": total_products,
                "active_products": active_products,
                "out_of_stock_products": out_of_stock_products,
                "total_orders": total_orders,
                "pending_orders": pending_orders,
                "total_revenue": total_revenue,
                "popular_products": popular_products,
                "recent_orders": recent_orders,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.order_list import OrderList
        from ..models.product_list import ProductList

        d = dict(src_dict)
        total_products = d.pop("total_products")

        active_products = d.pop("active_products")

        out_of_stock_products = d.pop("out_of_stock_products")

        total_orders = d.pop("total_orders")

        pending_orders = d.pop("pending_orders")

        total_revenue = d.pop("total_revenue")

        popular_products = []
        _popular_products = d.pop("popular_products")
        for popular_products_item_data in _popular_products:
            popular_products_item = ProductList.from_dict(popular_products_item_data)

            popular_products.append(popular_products_item)

        recent_orders = []
        _recent_orders = d.pop("recent_orders")
        for recent_orders_item_data in _recent_orders:
            recent_orders_item = OrderList.from_dict(recent_orders_item_data)

            recent_orders.append(recent_orders_item)

        shop_stats = cls(
            total_products=total_products,
            active_products=active_products,
            out_of_stock_products=out_of_stock_products,
            total_orders=total_orders,
            pending_orders=pending_orders,
            total_revenue=total_revenue,
            popular_products=popular_products,
            recent_orders=recent_orders,
        )

        shop_stats.additional_properties = d
        return shop_stats

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
