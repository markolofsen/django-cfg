from typing import *

from pydantic import BaseModel, Field

from .OrderItem import OrderItem
from .StatusA98Enum import StatusA98Enum


class OrderDetail(BaseModel):
    """
    None model
        Serializer for order detail view.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: int = Field(validation_alias="id")

    order_number: str = Field(validation_alias="order_number")

    customer: str = Field(validation_alias="customer")

    status: Optional[StatusA98Enum] = Field(validation_alias="status", default=None)

    subtotal: Optional[str] = Field(validation_alias="subtotal", default=None)

    tax_amount: Optional[str] = Field(validation_alias="tax_amount", default=None)

    shipping_amount: Optional[str] = Field(validation_alias="shipping_amount", default=None)

    discount_amount: Optional[str] = Field(validation_alias="discount_amount", default=None)

    total_amount: Optional[str] = Field(validation_alias="total_amount", default=None)

    billing_address: str = Field(validation_alias="billing_address")

    shipping_address: str = Field(validation_alias="shipping_address")

    customer_notes: Optional[str] = Field(validation_alias="customer_notes", default=None)

    admin_notes: Optional[str] = Field(validation_alias="admin_notes", default=None)

    items: List[OrderItem] = Field(validation_alias="items")

    created_at: str = Field(validation_alias="created_at")

    updated_at: str = Field(validation_alias="updated_at")

    shipped_at: Optional[str] = Field(validation_alias="shipped_at", default=None)

    delivered_at: Optional[str] = Field(validation_alias="delivered_at", default=None)
