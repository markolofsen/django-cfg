from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.email_log_status import check_email_log_status
from ..models.email_log_status import EmailLogStatus
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from uuid import UUID
import datetime


T = TypeVar("T", bound="EmailLog")


@_attrs_define
class EmailLog:
    """Serializer for EmailLog model.

    Attributes:
        id (UUID):
        user (Union[None, int]):
        user_email (str):
        newsletter (Union[None, int]):
        newsletter_title (str):
        recipient (str): Comma-separated email addresses
        subject (str):
        body (str):
        status (EmailLogStatus): * `pending` - Pending
            * `sent` - Sent
            * `failed` - Failed
        created_at (datetime.datetime):
        sent_at (Union[None, datetime.datetime]):
        error_message (Union[None, str]):
    """

    id: UUID
    user: Union[None, int]
    user_email: str
    newsletter: Union[None, int]
    newsletter_title: str
    recipient: str
    subject: str
    body: str
    status: EmailLogStatus
    created_at: datetime.datetime
    sent_at: Union[None, datetime.datetime]
    error_message: Union[None, str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        user: Union[None, int]
        user = self.user

        user_email = self.user_email

        newsletter: Union[None, int]
        newsletter = self.newsletter

        newsletter_title = self.newsletter_title

        recipient = self.recipient

        subject = self.subject

        body = self.body

        status: str = self.status

        created_at = self.created_at.isoformat()

        sent_at: Union[None, str]
        if isinstance(self.sent_at, datetime.datetime):
            sent_at = self.sent_at.isoformat()
        else:
            sent_at = self.sent_at

        error_message: Union[None, str]
        error_message = self.error_message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "user": user,
                "user_email": user_email,
                "newsletter": newsletter,
                "newsletter_title": newsletter_title,
                "recipient": recipient,
                "subject": subject,
                "body": body,
                "status": status,
                "created_at": created_at,
                "sent_at": sent_at,
                "error_message": error_message,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        def _parse_user(data: object) -> Union[None, int]:
            if data is None:
                return data
            return cast(Union[None, int], data)

        user = _parse_user(d.pop("user"))

        user_email = d.pop("user_email")

        def _parse_newsletter(data: object) -> Union[None, int]:
            if data is None:
                return data
            return cast(Union[None, int], data)

        newsletter = _parse_newsletter(d.pop("newsletter"))

        newsletter_title = d.pop("newsletter_title")

        recipient = d.pop("recipient")

        subject = d.pop("subject")

        body = d.pop("body")

        status = check_email_log_status(d.pop("status"))

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

        def _parse_error_message(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        error_message = _parse_error_message(d.pop("error_message"))

        email_log = cls(
            id=id,
            user=user,
            user_email=user_email,
            newsletter=newsletter,
            newsletter_title=newsletter_title,
            recipient=recipient,
            subject=subject,
            body=body,
            status=status,
            created_at=created_at,
            sent_at=sent_at,
            error_message=error_message,
        )

        email_log.additional_properties = d
        return email_log

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
