from typing import Literal, cast

TicketRequestStatus = Literal["closed", "open", "resolved", "waiting_for_admin", "waiting_for_user"]

TICKET_REQUEST_STATUS_VALUES: set[TicketRequestStatus] = {
    "closed",
    "open",
    "resolved",
    "waiting_for_admin",
    "waiting_for_user",
}


def check_ticket_request_status(value: str) -> TicketRequestStatus:
    if value in TICKET_REQUEST_STATUS_VALUES:
        return cast(TicketRequestStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TICKET_REQUEST_STATUS_VALUES!r}")
