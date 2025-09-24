from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.newsletter_campaign_status import check_newsletter_campaign_status
from ..models.newsletter_campaign_status import NewsletterCampaignStatus
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
import datetime


T = TypeVar("T", bound="NewsletterCampaign")


@_attrs_define
class NewsletterCampaign:
    """Serializer for NewsletterCampaign model.

    Attributes:
        id (int):
        newsletter (int):
        newsletter_title (str):
        subject (str):
        email_title (str):
        main_text (str):
        status (NewsletterCampaignStatus): * `draft` - Draft
            * `sending` - Sending
            * `sent` - Sent
            * `failed` - Failed
        created_at (datetime.datetime):
        sent_at (Union[None, datetime.datetime]):
        recipient_count (int):
        main_html_content (Union[Unset, str]):
        button_text (Union[Unset, str]):
        button_url (Union[Unset, str]):
        secondary_text (Union[Unset, str]):
    """

    id: int
    newsletter: int
    newsletter_title: str
    subject: str
    email_title: str
    main_text: str
    status: NewsletterCampaignStatus
    created_at: datetime.datetime
    sent_at: Union[None, datetime.datetime]
    recipient_count: int
    main_html_content: Union[Unset, str] = UNSET
    button_text: Union[Unset, str] = UNSET
    button_url: Union[Unset, str] = UNSET
    secondary_text: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        newsletter = self.newsletter

        newsletter_title = self.newsletter_title

        subject = self.subject

        email_title = self.email_title

        main_text = self.main_text

        status: str = self.status

        created_at = self.created_at.isoformat()

        sent_at: Union[None, str]
        if isinstance(self.sent_at, datetime.datetime):
            sent_at = self.sent_at.isoformat()
        else:
            sent_at = self.sent_at

        recipient_count = self.recipient_count

        main_html_content = self.main_html_content

        button_text = self.button_text

        button_url = self.button_url

        secondary_text = self.secondary_text

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "newsletter": newsletter,
                "newsletter_title": newsletter_title,
                "subject": subject,
                "email_title": email_title,
                "main_text": main_text,
                "status": status,
                "created_at": created_at,
                "sent_at": sent_at,
                "recipient_count": recipient_count,
            }
        )
        if main_html_content is not UNSET:
            field_dict["main_html_content"] = main_html_content
        if button_text is not UNSET:
            field_dict["button_text"] = button_text
        if button_url is not UNSET:
            field_dict["button_url"] = button_url
        if secondary_text is not UNSET:
            field_dict["secondary_text"] = secondary_text

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        newsletter = d.pop("newsletter")

        newsletter_title = d.pop("newsletter_title")

        subject = d.pop("subject")

        email_title = d.pop("email_title")

        main_text = d.pop("main_text")

        status = check_newsletter_campaign_status(d.pop("status"))

        created_at = isoparse(d.pop("created_at"))

        def _parse_sent_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                sent_at_type_0 = isoparse(data)

                return sent_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        sent_at = _parse_sent_at(d.pop("sent_at"))

        recipient_count = d.pop("recipient_count")

        main_html_content = d.pop("main_html_content", UNSET)

        button_text = d.pop("button_text", UNSET)

        button_url = d.pop("button_url", UNSET)

        secondary_text = d.pop("secondary_text", UNSET)

        newsletter_campaign = cls(
            id=id,
            newsletter=newsletter,
            newsletter_title=newsletter_title,
            subject=subject,
            email_title=email_title,
            main_text=main_text,
            status=status,
            created_at=created_at,
            sent_at=sent_at,
            recipient_count=recipient_count,
            main_html_content=main_html_content,
            button_text=button_text,
            button_url=button_url,
            secondary_text=secondary_text,
        )

        newsletter_campaign.additional_properties = d
        return newsletter_campaign

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
