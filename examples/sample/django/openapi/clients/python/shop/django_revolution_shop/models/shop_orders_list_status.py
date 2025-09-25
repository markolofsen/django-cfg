from typing import Literal, cast

ShopOrdersListStatus = Literal["cancelled", "delivered", "pending", "processing", "refunded", "shipped"]

SHOP_ORDERS_LIST_STATUS_VALUES: set[ShopOrdersListStatus] = {
    "cancelled",
    "delivered",
    "pending",
    "processing",
    "refunded",
    "shipped",
}


def check_shop_orders_list_status(value: str) -> ShopOrdersListStatus:
    if value in SHOP_ORDERS_LIST_STATUS_VALUES:
        return cast(ShopOrdersListStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {SHOP_ORDERS_LIST_STATUS_VALUES!r}")
