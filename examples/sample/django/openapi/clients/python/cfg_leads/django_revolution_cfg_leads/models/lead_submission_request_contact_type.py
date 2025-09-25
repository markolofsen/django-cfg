from typing import Literal, cast

LeadSubmissionRequestContactType = Literal["email", "other", "phone", "telegram", "whatsapp"]

LEAD_SUBMISSION_REQUEST_CONTACT_TYPE_VALUES: set[LeadSubmissionRequestContactType] = {
    "email",
    "other",
    "phone",
    "telegram",
    "whatsapp",
}


def check_lead_submission_request_contact_type(value: str) -> LeadSubmissionRequestContactType:
    if value in LEAD_SUBMISSION_REQUEST_CONTACT_TYPE_VALUES:
        return cast(LeadSubmissionRequestContactType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {LEAD_SUBMISSION_REQUEST_CONTACT_TYPE_VALUES!r}")
