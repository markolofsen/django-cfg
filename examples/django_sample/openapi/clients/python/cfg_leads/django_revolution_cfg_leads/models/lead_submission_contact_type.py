from typing import Literal, cast

LeadSubmissionContactType = Literal["email", "other", "phone", "telegram", "whatsapp"]

LEAD_SUBMISSION_CONTACT_TYPE_VALUES: set[LeadSubmissionContactType] = {
    "email",
    "other",
    "phone",
    "telegram",
    "whatsapp",
}


def check_lead_submission_contact_type(value: str) -> LeadSubmissionContactType:
    if value in LEAD_SUBMISSION_CONTACT_TYPE_VALUES:
        return cast(LeadSubmissionContactType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {LEAD_SUBMISSION_CONTACT_TYPE_VALUES!r}")
