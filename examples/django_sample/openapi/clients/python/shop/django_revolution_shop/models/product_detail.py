from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.product_detail_status import check_product_detail_status
from ..models.product_detail_status import ProductDetailStatus
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
import datetime

if TYPE_CHECKING:
    from ..models.category import Category


T = TypeVar("T", bound="ProductDetail")


@_attrs_define
class ProductDetail:
    """Serializer for product detail view.

    Attributes:
        id (int):
        name (str):
        description (str):
        price (str):
        current_price (str):
        is_on_sale (bool):
        discount_percentage (int):
        sku (str):
        is_in_stock (bool):
        category (Category): Serializer for shop categories.
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        slug (Union[Unset, str]):
        short_description (Union[Unset, str]):
        sale_price (Union[None, Unset, str]):
        stock_quantity (Union[Unset, int]):
        manage_stock (Union[Unset, bool]):
        image (Union[None, Unset, str]):
        status (Union[Unset, ProductDetailStatus]): * `active` - Active
            * `inactive` - Inactive
            * `out_of_stock` - Out of Stock
        is_featured (Union[Unset, bool]):
        is_digital (Union[Unset, bool]):
        meta_title (Union[Unset, str]):
        meta_description (Union[Unset, str]):
        views_count (Union[Unset, int]):
        sales_count (Union[Unset, int]):
        weight (Union[None, Unset, str]): Weight in kg
        length (Union[None, Unset, str]): Length in cm
        width (Union[None, Unset, str]): Width in cm
        height (Union[None, Unset, str]): Height in cm
    """

    id: int
    name: str
    description: str
    price: str
    current_price: str
    is_on_sale: bool
    discount_percentage: int
    sku: str
    is_in_stock: bool
    category: "Category"
    created_at: datetime.datetime
    updated_at: datetime.datetime
    slug: Union[Unset, str] = UNSET
    short_description: Union[Unset, str] = UNSET
    sale_price: Union[None, Unset, str] = UNSET
    stock_quantity: Union[Unset, int] = UNSET
    manage_stock: Union[Unset, bool] = UNSET
    image: Union[None, Unset, str] = UNSET
    status: Union[Unset, ProductDetailStatus] = UNSET
    is_featured: Union[Unset, bool] = UNSET
    is_digital: Union[Unset, bool] = UNSET
    meta_title: Union[Unset, str] = UNSET
    meta_description: Union[Unset, str] = UNSET
    views_count: Union[Unset, int] = UNSET
    sales_count: Union[Unset, int] = UNSET
    weight: Union[None, Unset, str] = UNSET
    length: Union[None, Unset, str] = UNSET
    width: Union[None, Unset, str] = UNSET
    height: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.category import Category

        id = self.id

        name = self.name

        description = self.description

        price = self.price

        current_price = self.current_price

        is_on_sale = self.is_on_sale

        discount_percentage = self.discount_percentage

        sku = self.sku

        is_in_stock = self.is_in_stock

        category = self.category.to_dict()

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        slug = self.slug

        short_description = self.short_description

        sale_price: Union[None, Unset, str]
        if isinstance(self.sale_price, Unset):
            sale_price = UNSET
        else:
            sale_price = self.sale_price

        stock_quantity = self.stock_quantity

        manage_stock = self.manage_stock

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

        meta_title = self.meta_title

        meta_description = self.meta_description

        views_count = self.views_count

        sales_count = self.sales_count

        weight: Union[None, Unset, str]
        if isinstance(self.weight, Unset):
            weight = UNSET
        else:
            weight = self.weight

        length: Union[None, Unset, str]
        if isinstance(self.length, Unset):
            length = UNSET
        else:
            length = self.length

        width: Union[None, Unset, str]
        if isinstance(self.width, Unset):
            width = UNSET
        else:
            width = self.width

        height: Union[None, Unset, str]
        if isinstance(self.height, Unset):
            height = UNSET
        else:
            height = self.height

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "price": price,
                "current_price": current_price,
                "is_on_sale": is_on_sale,
                "discount_percentage": discount_percentage,
                "sku": sku,
                "is_in_stock": is_in_stock,
                "category": category,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if slug is not UNSET:
            field_dict["slug"] = slug
        if short_description is not UNSET:
            field_dict["short_description"] = short_description
        if sale_price is not UNSET:
            field_dict["sale_price"] = sale_price
        if stock_quantity is not UNSET:
            field_dict["stock_quantity"] = stock_quantity
        if manage_stock is not UNSET:
            field_dict["manage_stock"] = manage_stock
        if image is not UNSET:
            field_dict["image"] = image
        if status is not UNSET:
            field_dict["status"] = status
        if is_featured is not UNSET:
            field_dict["is_featured"] = is_featured
        if is_digital is not UNSET:
            field_dict["is_digital"] = is_digital
        if meta_title is not UNSET:
            field_dict["meta_title"] = meta_title
        if meta_description is not UNSET:
            field_dict["meta_description"] = meta_description
        if views_count is not UNSET:
            field_dict["views_count"] = views_count
        if sales_count is not UNSET:
            field_dict["sales_count"] = sales_count
        if weight is not UNSET:
            field_dict["weight"] = weight
        if length is not UNSET:
            field_dict["length"] = length
        if width is not UNSET:
            field_dict["width"] = width
        if height is not UNSET:
            field_dict["height"] = height

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.category import Category

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        price = d.pop("price")

        current_price = d.pop("current_price")

        is_on_sale = d.pop("is_on_sale")

        discount_percentage = d.pop("discount_percentage")

        sku = d.pop("sku")

        is_in_stock = d.pop("is_in_stock")

        category = Category.from_dict(d.pop("category"))

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        slug = d.pop("slug", UNSET)

        short_description = d.pop("short_description", UNSET)

        def _parse_sale_price(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        sale_price = _parse_sale_price(d.pop("sale_price", UNSET))

        stock_quantity = d.pop("stock_quantity", UNSET)

        manage_stock = d.pop("manage_stock", UNSET)

        def _parse_image(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        image = _parse_image(d.pop("image", UNSET))

        _status = d.pop("status", UNSET)
        status: Union[Unset, ProductDetailStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = check_product_detail_status(_status)

        is_featured = d.pop("is_featured", UNSET)

        is_digital = d.pop("is_digital", UNSET)

        meta_title = d.pop("meta_title", UNSET)

        meta_description = d.pop("meta_description", UNSET)

        views_count = d.pop("views_count", UNSET)

        sales_count = d.pop("sales_count", UNSET)

        def _parse_weight(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        weight = _parse_weight(d.pop("weight", UNSET))

        def _parse_length(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        length = _parse_length(d.pop("length", UNSET))

        def _parse_width(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        width = _parse_width(d.pop("width", UNSET))

        def _parse_height(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        height = _parse_height(d.pop("height", UNSET))

        product_detail = cls(
            id=id,
            name=name,
            description=description,
            price=price,
            current_price=current_price,
            is_on_sale=is_on_sale,
            discount_percentage=discount_percentage,
            sku=sku,
            is_in_stock=is_in_stock,
            category=category,
            created_at=created_at,
            updated_at=updated_at,
            slug=slug,
            short_description=short_description,
            sale_price=sale_price,
            stock_quantity=stock_quantity,
            manage_stock=manage_stock,
            image=image,
            status=status,
            is_featured=is_featured,
            is_digital=is_digital,
            meta_title=meta_title,
            meta_description=meta_description,
            views_count=views_count,
            sales_count=sales_count,
            weight=weight,
            length=length,
            width=width,
            height=height,
        )

        product_detail.additional_properties = d
        return product_detail

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
