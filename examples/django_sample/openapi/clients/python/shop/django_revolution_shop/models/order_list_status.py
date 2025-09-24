from typing import Literal, cast

OrderListStatus = Literal["cancelled", "delivered", "pending", "processing", "refunded", "shipped"]

ORDER_LIST_STATUS_VALUES: set[OrderListStatus] = {
    "cancelled",
    "delivered",
    "pending",
    "processing",
    "refunded",
    "shipped",
}


def check_order_list_status(value: str) -> OrderListStatus:
    if value in ORDER_LIST_STATUS_VALUES:
        return cast(OrderListStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {ORDER_LIST_STATUS_VALUES!r}")
