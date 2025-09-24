from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field
import json
from .. import types

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union


T = TypeVar("T", bound="PatchedNewsletterCampaignRequest")


@_attrs_define
class PatchedNewsletterCampaignRequest:
    """Serializer for NewsletterCampaign model.

    Attributes:
        newsletter (Union[Unset, int]):
        subject (Union[Unset, str]):
        email_title (Union[Unset, str]):
        main_text (Union[Unset, str]):
        main_html_content (Union[Unset, str]):
        button_text (Union[Unset, str]):
        button_url (Union[Unset, str]):
        secondary_text (Union[Unset, str]):
    """

    newsletter: Union[Unset, int] = UNSET
    subject: Union[Unset, str] = UNSET
    email_title: Union[Unset, str] = UNSET
    main_text: Union[Unset, str] = UNSET
    main_html_content: Union[Unset, str] = UNSET
    button_text: Union[Unset, str] = UNSET
    button_url: Union[Unset, str] = UNSET
    secondary_text: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        newsletter = self.newsletter

        subject = self.subject

        email_title = self.email_title

        main_text = self.main_text

        main_html_content = self.main_html_content

        button_text = self.button_text

        button_url = self.button_url

        secondary_text = self.secondary_text

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if newsletter is not UNSET:
            field_dict["newsletter"] = newsletter
        if subject is not UNSET:
            field_dict["subject"] = subject
        if email_title is not UNSET:
            field_dict["email_title"] = email_title
        if main_text is not UNSET:
            field_dict["main_text"] = main_text
        if main_html_content is not UNSET:
            field_dict["main_html_content"] = main_html_content
        if button_text is not UNSET:
            field_dict["button_text"] = button_text
        if button_url is not UNSET:
            field_dict["button_url"] = button_url
        if secondary_text is not UNSET:
            field_dict["secondary_text"] = secondary_text

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        if not isinstance(self.newsletter, Unset):
            files.append(("newsletter", (None, str(self.newsletter).encode(), "text/plain")))

        if not isinstance(self.subject, Unset):
            files.append(("subject", (None, str(self.subject).encode(), "text/plain")))

        if not isinstance(self.email_title, Unset):
            files.append(("email_title", (None, str(self.email_title).encode(), "text/plain")))

        if not isinstance(self.main_text, Unset):
            files.append(("main_text", (None, str(self.main_text).encode(), "text/plain")))

        if not isinstance(self.main_html_content, Unset):
            files.append(("main_html_content", (None, str(self.main_html_content).encode(), "text/plain")))

        if not isinstance(self.button_text, Unset):
            files.append(("button_text", (None, str(self.button_text).encode(), "text/plain")))

        if not isinstance(self.button_url, Unset):
            files.append(("button_url", (None, str(self.button_url).encode(), "text/plain")))

        if not isinstance(self.secondary_text, Unset):
            files.append(("secondary_text", (None, str(self.secondary_text).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        newsletter = d.pop("newsletter", UNSET)

        subject = d.pop("subject", UNSET)

        email_title = d.pop("email_title", UNSET)

        main_text = d.pop("main_text", UNSET)

        main_html_content = d.pop("main_html_content", UNSET)

        button_text = d.pop("button_text", UNSET)

        button_url = d.pop("button_url", UNSET)

        secondary_text = d.pop("secondary_text", UNSET)

        patched_newsletter_campaign_request = cls(
            newsletter=newsletter,
            subject=subject,
            email_title=email_title,
            main_text=main_text,
            main_html_content=main_html_content,
            button_text=button_text,
            button_url=button_url,
            secondary_text=secondary_text,
        )

        patched_newsletter_campaign_request.additional_properties = d
        return patched_newsletter_campaign_request

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
