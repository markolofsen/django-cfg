from typing import Literal, cast

OrderDetailStatus = Literal["cancelled", "delivered", "pending", "processing", "refunded", "shipped"]

ORDER_DETAIL_STATUS_VALUES: set[OrderDetailStatus] = {
    "cancelled",
    "delivered",
    "pending",
    "processing",
    "refunded",
    "shipped",
}


def check_order_detail_status(value: str) -> OrderDetailStatus:
    if value in ORDER_DETAIL_STATUS_VALUES:
        return cast(OrderDetailStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {ORDER_DETAIL_STATUS_VALUES!r}")
