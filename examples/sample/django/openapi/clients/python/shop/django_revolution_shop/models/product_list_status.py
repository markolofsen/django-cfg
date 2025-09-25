from typing import Literal, cast

ProductListStatus = Literal["active", "inactive", "out_of_stock"]

PRODUCT_LIST_STATUS_VALUES: set[ProductListStatus] = {
    "active",
    "inactive",
    "out_of_stock",
}


def check_product_list_status(value: str) -> ProductListStatus:
    if value in PRODUCT_LIST_STATUS_VALUES:
        return cast(ProductListStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PRODUCT_LIST_STATUS_VALUES!r}")
