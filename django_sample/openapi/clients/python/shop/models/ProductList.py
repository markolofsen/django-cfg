from typing import *

from pydantic import BaseModel, Field

from .Category import Category
from .Status50eEnum import Status50eEnum


class ProductList(BaseModel):
    """
    None model
        Serializer for product list view.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: int = Field(validation_alias="id")

    name: str = Field(validation_alias="name")

    slug: Optional[str] = Field(validation_alias="slug", default=None)

    short_description: Optional[str] = Field(validation_alias="short_description", default=None)

    price: str = Field(validation_alias="price")

    sale_price: Optional[str] = Field(validation_alias="sale_price", default=None)

    current_price: str = Field(validation_alias="current_price")

    is_on_sale: bool = Field(validation_alias="is_on_sale")

    discount_percentage: int = Field(validation_alias="discount_percentage")

    category: Category = Field(validation_alias="category")

    image: Optional[str] = Field(validation_alias="image", default=None)

    status: Optional[Status50eEnum] = Field(validation_alias="status", default=None)

    is_featured: Optional[bool] = Field(validation_alias="is_featured", default=None)

    is_digital: Optional[bool] = Field(validation_alias="is_digital", default=None)

    stock_quantity: Optional[int] = Field(validation_alias="stock_quantity", default=None)

    is_in_stock: bool = Field(validation_alias="is_in_stock")

    views_count: Optional[int] = Field(validation_alias="views_count", default=None)

    sales_count: Optional[int] = Field(validation_alias="sales_count", default=None)

    created_at: str = Field(validation_alias="created_at")
