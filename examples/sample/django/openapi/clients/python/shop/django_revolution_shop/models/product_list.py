from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.product_list_status import check_product_list_status
from ..models.product_list_status import ProductListStatus
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
import datetime

if TYPE_CHECKING:
    from ..models.category import Category


T = TypeVar("T", bound="ProductList")


@_attrs_define
class ProductList:
    """Serializer for product list view.

    Attributes:
        id (int):
        name (str):
        price (str):
        current_price (str):
        is_on_sale (bool):
        discount_percentage (int):
        category (Category): Serializer for shop categories.
        is_in_stock (bool):
        created_at (datetime.datetime):
        slug (Union[Unset, str]):
        short_description (Union[Unset, str]):
        sale_price (Union[None, Unset, str]):
        image (Union[None, Unset, str]):
        status (Union[Unset, ProductListStatus]): * `active` - Active
            * `inactive` - Inactive
            * `out_of_stock` - Out of Stock
        is_featured (Union[Unset, bool]):
        is_digital (Union[Unset, bool]):
        stock_quantity (Union[Unset, int]):
        views_count (Union[Unset, int]):
        sales_count (Union[Unset, int]):
    """

    id: int
    name: str
    price: str
    current_price: str
    is_on_sale: bool
    discount_percentage: int
    category: "Category"
    is_in_stock: bool
    created_at: datetime.datetime
    slug: Union[Unset, str] = UNSET
    short_description: Union[Unset, str] = UNSET
    sale_price: Union[None, Unset, str] = UNSET
    image: Union[None, Unset, str] = UNSET
    status: Union[Unset, ProductListStatus] = UNSET
    is_featured: Union[Unset, bool] = UNSET
    is_digital: Union[Unset, bool] = UNSET
    stock_quantity: Union[Unset, int] = UNSET
    views_count: Union[Unset, int] = UNSET
    sales_count: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.category import Category

        id = self.id

        name = self.name

        price = self.price

        current_price = self.current_price

        is_on_sale = self.is_on_sale

        discount_percentage = self.discount_percentage

        category = self.category.to_dict()

        is_in_stock = self.is_in_stock

        created_at = self.created_at.isoformat()

        slug = self.slug

        short_description = self.short_description

        sale_price: Union[None, Unset, str]
        if isinstance(self.sale_price, Unset):
            sale_price = UNSET
        else:
            sale_price = self.sale_price

        image: Union[None, Unset, str]
        if isinstance(self.image, Unset):
            image = UNSET
        else:
            image = self.image

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status

        is_featured = self.is_featured

        is_digital = self.is_digital

        stock_quantity = self.stock_quantity

        views_count = self.views_count

        sales_count = self.sales_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "price": price,
                "current_price": current_price,
                "is_on_sale": is_on_sale,
                "discount_percentage": discount_percentage,
                "category": category,
                "is_in_stock": is_in_stock,
                "created_at": created_at,
            }
        )
        if slug is not UNSET:
            field_dict["slug"] = slug
        if short_description is not UNSET:
            field_dict["short_description"] = short_description
        if sale_price is not UNSET:
            field_dict["sale_price"] = sale_price
        if image is not UNSET:
            field_dict["image"] = image
        if status is not UNSET:
            field_dict["status"] = status
        if is_featured is not UNSET:
            field_dict["is_featured"] = is_featured
        if is_digital is not UNSET:
            field_dict["is_digital"] = is_digital
        if stock_quantity is not UNSET:
            field_dict["stock_quantity"] = stock_quantity
        if views_count is not UNSET:
            field_dict["views_count"] = views_count
        if sales_count is not UNSET:
            field_dict["sales_count"] = sales_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.category import Category

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        price = d.pop("price")

        current_price = d.pop("current_price")

        is_on_sale = d.pop("is_on_sale")

        discount_percentage = d.pop("discount_percentage")

        category = Category.from_dict(d.pop("category"))

        is_in_stock = d.pop("is_in_stock")

        created_at = isoparse(d.pop("created_at"))

        slug = d.pop("slug", UNSET)

        short_description = d.pop("short_description", UNSET)

        def _parse_sale_price(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        sale_price = _parse_sale_price(d.pop("sale_price", UNSET))

        def _parse_image(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        image = _parse_image(d.pop("image", UNSET))

        _status = d.pop("status", UNSET)
        status: Union[Unset, ProductListStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = check_product_list_status(_status)

        is_featured = d.pop("is_featured", UNSET)

        is_digital = d.pop("is_digital", UNSET)

        stock_quantity = d.pop("stock_quantity", UNSET)

        views_count = d.pop("views_count", UNSET)

        sales_count = d.pop("sales_count", UNSET)

        product_list = cls(
            id=id,
            name=name,
            price=price,
            current_price=current_price,
            is_on_sale=is_on_sale,
            discount_percentage=discount_percentage,
            category=category,
            is_in_stock=is_in_stock,
            created_at=created_at,
            slug=slug,
            short_description=short_description,
            sale_price=sale_price,
            image=image,
            status=status,
            is_featured=is_featured,
            is_digital=is_digital,
            stock_quantity=stock_quantity,
            views_count=views_count,
            sales_count=sales_count,
        )

        product_list.additional_properties = d
        return product_list

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
