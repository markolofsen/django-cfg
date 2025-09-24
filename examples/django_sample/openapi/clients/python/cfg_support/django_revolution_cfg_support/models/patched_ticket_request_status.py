from typing import Literal, cast

PatchedTicketRequestStatus = Literal["closed", "open", "resolved", "waiting_for_admin", "waiting_for_user"]

PATCHED_TICKET_REQUEST_STATUS_VALUES: set[PatchedTicketRequestStatus] = {
    "closed",
    "open",
    "resolved",
    "waiting_for_admin",
    "waiting_for_user",
}


def check_patched_ticket_request_status(value: str) -> PatchedTicketRequestStatus:
    if value in PATCHED_TICKET_REQUEST_STATUS_VALUES:
        return cast(PatchedTicketRequestStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PATCHED_TICKET_REQUEST_STATUS_VALUES!r}")
