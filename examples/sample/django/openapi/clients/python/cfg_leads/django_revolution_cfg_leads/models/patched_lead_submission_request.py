from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field
import json
from .. import types

from ..types import UNSET, Unset

from ..models.patched_lead_submission_request_contact_type import check_patched_lead_submission_request_contact_type
from ..models.patched_lead_submission_request_contact_type import PatchedLeadSubmissionRequestContactType
from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union


T = TypeVar("T", bound="PatchedLeadSubmissionRequest")


@_attrs_define
class PatchedLeadSubmissionRequest:
    """Serializer for lead form submission from frontend.

    Attributes:
        name (Union[Unset, str]):
        email (Union[Unset, str]):
        company (Union[None, Unset, str]):
        company_site (Union[None, Unset, str]):
        contact_type (Union[Unset, PatchedLeadSubmissionRequestContactType]): * `email` - Email
            * `whatsapp` - WhatsApp
            * `telegram` - Telegram
            * `phone` - Phone
            * `other` - Other
        contact_value (Union[None, Unset, str]):
        subject (Union[None, Unset, str]):
        message (Union[Unset, str]):
        extra (Union[Unset, Any]):
        site_url (Union[Unset, str]): Frontend URL where form was submitted
    """

    name: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    company: Union[None, Unset, str] = UNSET
    company_site: Union[None, Unset, str] = UNSET
    contact_type: Union[Unset, PatchedLeadSubmissionRequestContactType] = UNSET
    contact_value: Union[None, Unset, str] = UNSET
    subject: Union[None, Unset, str] = UNSET
    message: Union[Unset, str] = UNSET
    extra: Union[Unset, Any] = UNSET
    site_url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        email = self.email

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

        message = self.message

        extra = self.extra

        site_url = self.site_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if email is not UNSET:
            field_dict["email"] = email
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
        if message is not UNSET:
            field_dict["message"] = message
        if extra is not UNSET:
            field_dict["extra"] = extra
        if site_url is not UNSET:
            field_dict["site_url"] = site_url

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        if not isinstance(self.name, Unset):
            files.append(("name", (None, str(self.name).encode(), "text/plain")))

        if not isinstance(self.email, Unset):
            files.append(("email", (None, str(self.email).encode(), "text/plain")))

        if not isinstance(self.company, Unset):
            if isinstance(self.company, str):
                files.append(("company", (None, str(self.company).encode(), "text/plain")))
            else:
                files.append(("company", (None, str(self.company).encode(), "text/plain")))

        if not isinstance(self.company_site, Unset):
            if isinstance(self.company_site, str):
                files.append(("company_site", (None, str(self.company_site).encode(), "text/plain")))
            else:
                files.append(("company_site", (None, str(self.company_site).encode(), "text/plain")))

        if not isinstance(self.contact_type, Unset):
            files.append(("contact_type", (None, str(self.contact_type).encode(), "text/plain")))

        if not isinstance(self.contact_value, Unset):
            if isinstance(self.contact_value, str):
                files.append(("contact_value", (None, str(self.contact_value).encode(), "text/plain")))
            else:
                files.append(("contact_value", (None, str(self.contact_value).encode(), "text/plain")))

        if not isinstance(self.subject, Unset):
            if isinstance(self.subject, str):
                files.append(("subject", (None, str(self.subject).encode(), "text/plain")))
            else:
                files.append(("subject", (None, str(self.subject).encode(), "text/plain")))

        if not isinstance(self.message, Unset):
            files.append(("message", (None, str(self.message).encode(), "text/plain")))

        if not isinstance(self.extra, Unset):
            files.append(("extra", (None, str(self.extra).encode(), "text/plain")))

        if not isinstance(self.site_url, Unset):
            files.append(("site_url", (None, str(self.site_url).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        email = d.pop("email", UNSET)

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
        contact_type: Union[Unset, PatchedLeadSubmissionRequestContactType]
        if isinstance(_contact_type, Unset):
            contact_type = UNSET
        else:
            contact_type = check_patched_lead_submission_request_contact_type(_contact_type)

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

        message = d.pop("message", UNSET)

        extra = d.pop("extra", UNSET)

        site_url = d.pop("site_url", UNSET)

        patched_lead_submission_request = cls(
            name=name,
            email=email,
            company=company,
            company_site=company_site,
            contact_type=contact_type,
            contact_value=contact_value,
            subject=subject,
            message=message,
            extra=extra,
            site_url=site_url,
        )

        patched_lead_submission_request.additional_properties = d
        return patched_lead_submission_request

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
