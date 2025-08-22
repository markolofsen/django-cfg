from typing import *

from pydantic import BaseModel, Field

from .ProductList import ProductList


class OrderItem(BaseModel):
    """
    None model
        Serializer for order items.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: int = Field(validation_alias="id")

    product: ProductList = Field(validation_alias="product")

    quantity: Optional[int] = Field(validation_alias="quantity", default=None)

    unit_price: str = Field(validation_alias="unit_price")

    total_price: str = Field(validation_alias="total_price")

    product_name: str = Field(validation_alias="product_name")

    product_sku: str = Field(validation_alias="product_sku")

    created_at: str = Field(validation_alias="created_at")
