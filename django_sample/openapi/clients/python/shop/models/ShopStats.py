from typing import *

from pydantic import BaseModel, Field

from .OrderList import OrderList
from .ProductList import ProductList


class ShopStats(BaseModel):
    """
    None model
        Serializer for shop statistics.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    total_products: int = Field(validation_alias="total_products")

    active_products: int = Field(validation_alias="active_products")

    out_of_stock_products: int = Field(validation_alias="out_of_stock_products")

    total_orders: int = Field(validation_alias="total_orders")

    pending_orders: int = Field(validation_alias="pending_orders")

    total_revenue: str = Field(validation_alias="total_revenue")

    popular_products: List[ProductList] = Field(validation_alias="popular_products")

    recent_orders: List[OrderList] = Field(validation_alias="recent_orders")
