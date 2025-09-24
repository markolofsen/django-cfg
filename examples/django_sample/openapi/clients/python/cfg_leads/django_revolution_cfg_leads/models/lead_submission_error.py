from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
    from ..models.lead_submission_error_details import LeadSubmissionErrorDetails


T = TypeVar("T", bound="LeadSubmissionError")


@_attrs_define
class LeadSubmissionError:
    """Response serializer for lead submission errors.

    Attributes:
        success (bool):
        error (str):
        details (Union[Unset, LeadSubmissionErrorDetails]):
    """

    success: bool
    error: str
    details: Union[Unset, "LeadSubmissionErrorDetails"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.lead_submission_error_details import LeadSubmissionErrorDetails

        success = self.success

        error = self.error

        details: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.details, Unset):
            details = self.details.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "success": success,
                "error": error,
            }
        )
        if details is not UNSET:
            field_dict["details"] = details

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.lead_submission_error_details import LeadSubmissionErrorDetails

        d = dict(src_dict)
        success = d.pop("success")

        error = d.pop("error")

        _details = d.pop("details", UNSET)
        details: Union[Unset, LeadSubmissionErrorDetails]
        if isinstance(_details, Unset):
            details = UNSET
        else:
            details = LeadSubmissionErrorDetails.from_dict(_details)

        lead_submission_error = cls(
            success=success,
            error=error,
            details=details,
        )

        lead_submission_error.additional_properties = d
        return lead_submission_error

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
