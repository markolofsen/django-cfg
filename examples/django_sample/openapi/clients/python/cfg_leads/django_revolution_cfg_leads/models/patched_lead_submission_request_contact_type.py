from typing import Literal, cast

PatchedLeadSubmissionRequestContactType = Literal["email", "other", "phone", "telegram", "whatsapp"]

PATCHED_LEAD_SUBMISSION_REQUEST_CONTACT_TYPE_VALUES: set[PatchedLeadSubmissionRequestContactType] = {
    "email",
    "other",
    "phone",
    "telegram",
    "whatsapp",
}


def check_patched_lead_submission_request_contact_type(value: str) -> PatchedLeadSubmissionRequestContactType:
    if value in PATCHED_LEAD_SUBMISSION_REQUEST_CONTACT_TYPE_VALUES:
        return cast(PatchedLeadSubmissionRequestContactType, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {PATCHED_LEAD_SUBMISSION_REQUEST_CONTACT_TYPE_VALUES!r}"
    )
