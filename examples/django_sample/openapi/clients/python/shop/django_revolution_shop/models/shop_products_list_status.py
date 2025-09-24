from typing import Literal, cast

ShopProductsListStatus = Literal["active", "inactive", "out_of_stock"]

SHOP_PRODUCTS_LIST_STATUS_VALUES: set[ShopProductsListStatus] = {
    "active",
    "inactive",
    "out_of_stock",
}


def check_shop_products_list_status(value: str) -> ShopProductsListStatus:
    if value in SHOP_PRODUCTS_LIST_STATUS_VALUES:
        return cast(ShopProductsListStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {SHOP_PRODUCTS_LIST_STATUS_VALUES!r}")
