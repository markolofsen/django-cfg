"""
Typed models for the webmail deep-link feature.

The goal: after we email a login code to ``user@gmail.com``, hand the frontend a
ready-to-open URL that lands the user *directly* on a search for our message in
their webmail — so finding the code is one click, not a hunt through the inbox.

Nothing here does network I/O. Provider detection is a pure function of the
address domain (see :mod:`.providers`); the sender to search for is the
project's ``DEFAULT_FROM_EMAIL`` (resolved in :mod:`.service`).
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class WebmailProvider(str, Enum):
    """
    Known webmail providers.

    Value is a stable, frontend-friendly slug (also used to pick a brand icon).
    Do NOT rename existing values — the frontend maps them to icons and the
    OpenAPI enum is codegen'd into the API client.
    """

    GMAIL = "gmail"
    OUTLOOK = "outlook"
    YAHOO = "yahoo"
    ICLOUD = "icloud"
    PROTON = "proton"
    ZOHO = "zoho"
    AOL = "aol"
    FASTMAIL = "fastmail"
    GMX = "gmx"
    MAILCOM = "mailcom"
    MAIL_RU = "mail_ru"
    YANDEX = "yandex"
    RAMBLER = "rambler"
    QQ = "qq"
    NETEASE = "netease"
    SINA = "sina"
    ALIYUN = "aliyun"
    NAVER = "naver"
    DAUM = "daum"
    WEB_DE = "web_de"
    TONLINE = "tonline"
    SEZNAM = "seznam"
    WP_PL = "wp_pl"
    O2_PL = "o2_pl"
    INTERIA = "interia"
    LIBERO = "libero"
    VIRGILIO = "virgilio"
    ORANGE = "orange"
    LAPOSTE = "laposte"
    FREE_FR = "free_fr"
    SFR = "sfr"


class ProviderConfidence(str, Enum):
    """
    How trustworthy a provider's *search* deep-link is.

    - ``verified``: officially documented or long-stable (Gmail, Outlook business).
    - ``observed``: seen working in the wild, no official doc (Yahoo, Mail.ru, Yandex, AOL).
    - ``inbox_only``: no search deep-link exists; we can only open the inbox.

    We ship ``verified`` + ``observed`` search links and fall back to the inbox
    for everything else. ``guess``-level links are intentionally NOT shipped.
    """

    VERIFIED = "verified"
    OBSERVED = "observed"
    INBOX_ONLY = "inbox_only"


class ProviderSpec(BaseModel):
    """
    Static spec for one provider family, keyed by its domains in :mod:`.providers`.

    ``search_url_template`` / ``inbox_url_template`` use ``{sender}`` as the
    placeholder for the URL-encoded sender address. ``search_url_template`` is
    ``None`` for inbox-only providers.
    """

    model_config = {"frozen": True}

    provider: WebmailProvider
    label: str = Field(..., description="Human-facing provider name, e.g. 'Gmail'.")
    confidence: ProviderConfidence
    search_url_template: Optional[str] = Field(
        default=None,
        description="URL template with {sender} placeholder; None if search is unsupported.",
    )
    inbox_url_template: str = Field(
        ..., description="URL that opens the mailbox; used as fallback."
    )


class WebmailLink(BaseModel):
    """
    Resolved deep-link handed to the frontend.

    This is what the serializer exposes on the OTP-request response. When the
    domain is unknown (e.g. a corporate mailbox) we return ``None`` instead of a
    ``WebmailLink`` and the frontend simply shows no button.
    """

    provider: WebmailProvider = Field(..., description="Provider slug (also selects the icon).")
    provider_name: str = Field(..., description="Human-facing name, e.g. 'Gmail'.")
    url: str = Field(..., description="Absolute URL to open (search or inbox).")
    is_search: bool = Field(
        ..., description="True if the URL opens a sender-filtered search; False if it only opens the inbox."
    )
