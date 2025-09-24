from typing import Literal, cast

ProductDetailStatus = Literal["active", "inactive", "out_of_stock"]

PRODUCT_DETAIL_STATUS_VALUES: set[ProductDetailStatus] = {
    "active",
    "inactive",
    "out_of_stock",
}


def check_product_detail_status(value: str) -> ProductDetailStatus:
    if value in PRODUCT_DETAIL_STATUS_VALUES:
        return cast(ProductDetailStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PRODUCT_DETAIL_STATUS_VALUES!r}")
