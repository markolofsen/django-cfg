from typing import *

from pydantic import BaseModel, Field

from .Category import Category
from .Status50eEnum import Status50eEnum


class ProductDetail(BaseModel):
    """
    None model
        Serializer for product detail view.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: int = Field(validation_alias="id")

    name: str = Field(validation_alias="name")

    slug: Optional[str] = Field(validation_alias="slug", default=None)

    description: str = Field(validation_alias="description")

    short_description: Optional[str] = Field(validation_alias="short_description", default=None)

    price: str = Field(validation_alias="price")

    sale_price: Optional[str] = Field(validation_alias="sale_price", default=None)

    current_price: str = Field(validation_alias="current_price")

    is_on_sale: bool = Field(validation_alias="is_on_sale")

    discount_percentage: int = Field(validation_alias="discount_percentage")

    sku: str = Field(validation_alias="sku")

    stock_quantity: Optional[int] = Field(validation_alias="stock_quantity", default=None)

    manage_stock: Optional[bool] = Field(validation_alias="manage_stock", default=None)

    is_in_stock: bool = Field(validation_alias="is_in_stock")

    category: Category = Field(validation_alias="category")

    image: Optional[str] = Field(validation_alias="image", default=None)

    status: Optional[Status50eEnum] = Field(validation_alias="status", default=None)

    is_featured: Optional[bool] = Field(validation_alias="is_featured", default=None)

    is_digital: Optional[bool] = Field(validation_alias="is_digital", default=None)

    meta_title: Optional[str] = Field(validation_alias="meta_title", default=None)

    meta_description: Optional[str] = Field(validation_alias="meta_description", default=None)

    views_count: Optional[int] = Field(validation_alias="views_count", default=None)

    sales_count: Optional[int] = Field(validation_alias="sales_count", default=None)

    weight: Optional[str] = Field(validation_alias="weight", default=None)

    length: Optional[str] = Field(validation_alias="length", default=None)

    width: Optional[str] = Field(validation_alias="width", default=None)

    height: Optional[str] = Field(validation_alias="height", default=None)

    created_at: str = Field(validation_alias="created_at")

    updated_at: str = Field(validation_alias="updated_at")
