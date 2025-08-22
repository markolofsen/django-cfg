from typing import *

from pydantic import BaseModel, Field

from .StatusA98Enum import StatusA98Enum


class OrderList(BaseModel):
    """
    None model
        Serializer for order list view.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: int = Field(validation_alias="id")

    order_number: str = Field(validation_alias="order_number")

    customer: str = Field(validation_alias="customer")

    status: Optional[StatusA98Enum] = Field(validation_alias="status", default=None)

    subtotal: Optional[str] = Field(validation_alias="subtotal", default=None)

    total_amount: Optional[str] = Field(validation_alias="total_amount", default=None)

    items_count: str = Field(validation_alias="items_count")

    created_at: str = Field(validation_alias="created_at")

    updated_at: str = Field(validation_alias="updated_at")
