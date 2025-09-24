from typing import Literal, cast

TicketStatus = Literal["closed", "open", "resolved", "waiting_for_admin", "waiting_for_user"]

TICKET_STATUS_VALUES: set[TicketStatus] = {
    "closed",
    "open",
    "resolved",
    "waiting_for_admin",
    "waiting_for_user",
}


def check_ticket_status(value: str) -> TicketStatus:
    if value in TICKET_STATUS_VALUES:
        return cast(TicketStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TICKET_STATUS_VALUES!r}")
