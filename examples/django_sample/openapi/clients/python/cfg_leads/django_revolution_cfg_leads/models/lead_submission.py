from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.lead_submission_contact_type import check_lead_submission_contact_type
from ..models.lead_submission_contact_type import LeadSubmissionContactType
from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union


T = TypeVar("T", bound="LeadSubmission")


@_attrs_define
class LeadSubmission:
    """Serializer for lead form submission from frontend.

    Attributes:
        name (str):
        email (str):
        message (str):
        site_url (str): Frontend URL where form was submitted
        company (Union[None, Unset, str]):
        company_site (Union[None, Unset, str]):
        contact_type (Union[Unset, LeadSubmissionContactType]): * `email` - Email
            * `whatsapp` - WhatsApp
            * `telegram` - Telegram
            * `phone` - Phone
            * `other` - Other
        contact_value (Union[None, Unset, str]):
        subject (Union[None, Unset, str]):
        extra (Union[Unset, Any]):
    """

    name: str
    email: str
    message: str
    site_url: str
    company: Union[None, Unset, str] = UNSET
    company_site: Union[None, Unset, str] = UNSET
    contact_type: Union[Unset, LeadSubmissionContactType] = UNSET
    contact_value: Union[None, Unset, str] = UNSET
    subject: Union[None, Unset, str] = UNSET
    extra: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        email = self.email

        message = self.message

        site_url = self.site_url

        company: Union[None, Unset, str]
        if isinstance(self.company, Unset):
            company = UNSET
        else:
            company = self.company

        company_site: Union[None, Unset, str]
        if isinstance(self.company_site, Unset):
            company_site = UNSET
        else:
            company_site = self.company_site

        contact_type: Union[Unset, str] = UNSET
        if not isinstance(self.contact_type, Unset):
            contact_type = self.contact_type

        contact_value: Union[None, Unset, str]
        if isinstance(self.contact_value, Unset):
            contact_value = UNSET
        else:
            contact_value = self.contact_value

        subject: Union[None, Unset, str]
        if isinstance(self.subject, Unset):
            subject = UNSET
        else:
            subject = self.subject

        extra = self.extra

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "email": email,
                "message": message,
                "site_url": site_url,
            }
        )
        if company is not UNSET:
            field_dict["company"] = company
        if company_site is not UNSET:
            field_dict["company_site"] = company_site
        if contact_type is not UNSET:
            field_dict["contact_type"] = contact_type
        if contact_value is not UNSET:
            field_dict["contact_value"] = contact_value
        if subject is not UNSET:
            field_dict["subject"] = subject
        if extra is not UNSET:
            field_dict["extra"] = extra

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        email = d.pop("email")

        message = d.pop("message")

        site_url = d.pop("site_url")

        def _parse_company(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        company = _parse_company(d.pop("company", UNSET))

        def _parse_company_site(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        company_site = _parse_company_site(d.pop("company_site", UNSET))

        _contact_type = d.pop("contact_type", UNSET)
        contact_type: Union[Unset, LeadSubmissionContactType]
        if isinstance(_contact_type, Unset):
            contact_type = UNSET
        else:
            contact_type = check_lead_submission_contact_type(_contact_type)

        def _parse_contact_value(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        contact_value = _parse_contact_value(d.pop("contact_value", UNSET))

        def _parse_subject(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        subject = _parse_subject(d.pop("subject", UNSET))

        extra = d.pop("extra", UNSET)

        lead_submission = cls(
            name=name,
            email=email,
            message=message,
            site_url=site_url,
            company=company,
            company_site=company_site,
            contact_type=contact_type,
            contact_value=contact_value,
            subject=subject,
            extra=extra,
        )

        lead_submission.additional_properties = d
        return lead_submission

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
