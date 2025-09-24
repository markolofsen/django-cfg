from typing import Literal, cast

EmailLogStatus = Literal["failed", "pending", "sent"]

EMAIL_LOG_STATUS_VALUES: set[EmailLogStatus] = {
    "failed",
    "pending",
    "sent",
}


def check_email_log_status(value: str) -> EmailLogStatus:
    if value in EMAIL_LOG_STATUS_VALUES:
        return cast(EmailLogStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {EMAIL_LOG_STATUS_VALUES!r}")
