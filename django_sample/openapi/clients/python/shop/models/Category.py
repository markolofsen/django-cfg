from typing import *

from pydantic import BaseModel, Field


class Category(BaseModel):
    """
    None model
        Serializer for shop categories.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: int = Field(validation_alias="id")

    name: str = Field(validation_alias="name")

    slug: str = Field(validation_alias="slug")

    description: Optional[str] = Field(validation_alias="description", default=None)

    image: Optional[str] = Field(validation_alias="image", default=None)

    parent: Optional[int] = Field(validation_alias="parent", default=None)

    meta_title: Optional[str] = Field(validation_alias="meta_title", default=None)

    meta_description: Optional[str] = Field(validation_alias="meta_description", default=None)

    products_count: int = Field(validation_alias="products_count")

    children: str = Field(validation_alias="children")

    is_active: Optional[bool] = Field(validation_alias="is_active", default=None)

    sort_order: Optional[int] = Field(validation_alias="sort_order", default=None)

    created_at: str = Field(validation_alias="created_at")

    updated_at: str = Field(validation_alias="updated_at")
