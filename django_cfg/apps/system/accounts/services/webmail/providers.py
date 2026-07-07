"""
Static domain → provider mapping and per-provider URL templates.

Data compiled 2025-2026 from observed webmail routing. Confidence levels are
honest: only Gmail and Outlook (business) expose a *documented* sender-search
deep link; Yahoo / Mail.ru / Yandex / AOL search links are OBSERVED (work in
practice, no official doc); everything else is inbox-only.

Templates use ``{sender}`` for the URL-encoded sender address. ``from:`` is
pre-encoded as ``from%3A`` inside the templates so we only encode the address.

To add a provider: add a :class:`ProviderSpec` and list its domains in
``DOMAIN_TO_PROVIDER``. Lookup is exact-domain; unknown domains resolve to None.
"""

from __future__ import annotations

from typing import Dict

from .types import ProviderConfidence, ProviderSpec, WebmailProvider

# ---------------------------------------------------------------------------
# Per-provider specs
# ---------------------------------------------------------------------------

# Gmail: authuser={sender} selects the account by address (more robust than u/0
# when the user has multiple Google accounts — the common case is that the
# recipient mailbox IS the signed-in account).
_GMAIL = ProviderSpec(
    provider=WebmailProvider.GMAIL,
    label="Gmail",
    confidence=ProviderConfidence.VERIFIED,
    search_url_template="https://mail.google.com/mail/?authuser={sender}#search/from%3A{sender}",
    # Inbox fallback: no {sender} → use positional u/0 rather than an empty authuser=.
    inbox_url_template="https://mail.google.com/mail/u/0/#inbox",
)

# Outlook personal (outlook.com/hotmail/live/msn) — OWA "deeplink/search".
_OUTLOOK = ProviderSpec(
    provider=WebmailProvider.OUTLOOK,
    label="Outlook",
    confidence=ProviderConfidence.OBSERVED,
    search_url_template="https://outlook.live.com/mail/0/deeplink/search?query=from%3A{sender}",
    inbox_url_template="https://outlook.live.com/mail/0/",
)

_YAHOO = ProviderSpec(
    provider=WebmailProvider.YAHOO,
    label="Yahoo Mail",
    confidence=ProviderConfidence.OBSERVED,
    search_url_template="https://mail.yahoo.com/d/search/keyword=from%3A{sender}",
    inbox_url_template="https://mail.yahoo.com/d/folders/1",
)

_ICLOUD = ProviderSpec(
    provider=WebmailProvider.ICLOUD,
    label="iCloud Mail",
    confidence=ProviderConfidence.INBOX_ONLY,
    inbox_url_template="https://www.icloud.com/mail",
)

_PROTON = ProviderSpec(
    provider=WebmailProvider.PROTON,
    label="Proton Mail",
    confidence=ProviderConfidence.INBOX_ONLY,
    inbox_url_template="https://mail.proton.me/u/0/inbox",
)

_ZOHO = ProviderSpec(
    provider=WebmailProvider.ZOHO,
    label="Zoho Mail",
    confidence=ProviderConfidence.INBOX_ONLY,
    inbox_url_template="https://mail.zoho.com/zm/#mail/folder/inbox",
)

_AOL = ProviderSpec(
    provider=WebmailProvider.AOL,
    label="AOL Mail",
    confidence=ProviderConfidence.OBSERVED,
    search_url_template="https://mail.aol.com/d/search/keyword=from%3A{sender}",
    inbox_url_template="https://mail.aol.com/",
)

_FASTMAIL = ProviderSpec(
    provider=WebmailProvider.FASTMAIL,
    label="Fastmail",
    confidence=ProviderConfidence.INBOX_ONLY,
    inbox_url_template="https://app.fastmail.com/mail/Inbox",
)

_GMX = ProviderSpec(
    provider=WebmailProvider.GMX,
    label="GMX",
    confidence=ProviderConfidence.INBOX_ONLY,
    inbox_url_template="https://www.gmx.com/",
)

_MAILCOM = ProviderSpec(
    provider=WebmailProvider.MAILCOM,
    label="mail.com",
    confidence=ProviderConfidence.INBOX_ONLY,
    inbox_url_template="https://www.mail.com/",
)

_MAIL_RU = ProviderSpec(
    provider=WebmailProvider.MAIL_RU,
    label="Mail.ru",
    confidence=ProviderConfidence.OBSERVED,
    search_url_template="https://e.mail.ru/search/?q_from={sender}",
    inbox_url_template="https://e.mail.ru/inbox/",
)

_YANDEX = ProviderSpec(
    provider=WebmailProvider.YANDEX,
    label="Yandex Mail",
    confidence=ProviderConfidence.OBSERVED,
    search_url_template="https://mail.yandex.ru/#search?request=from%3A{sender}",
    inbox_url_template="https://mail.yandex.ru/#inbox",
)

_RAMBLER = ProviderSpec(
    provider=WebmailProvider.RAMBLER,
    label="Rambler Mail",
    confidence=ProviderConfidence.INBOX_ONLY,
    inbox_url_template="https://mail.rambler.ru/",
)

_QQ = ProviderSpec(
    provider=WebmailProvider.QQ,
    label="QQ Mail",
    confidence=ProviderConfidence.INBOX_ONLY,
    inbox_url_template="https://wx.mail.qq.com/",
)

# NetEase inbox host differs per domain; use the family default and let the
# provider-side redirect route the user. Most granular hosts share the login.
_NETEASE = ProviderSpec(
    provider=WebmailProvider.NETEASE,
    label="NetEase Mail",
    confidence=ProviderConfidence.INBOX_ONLY,
    inbox_url_template="https://mail.163.com/",
)

_SINA = ProviderSpec(
    provider=WebmailProvider.SINA,
    label="Sina Mail",
    confidence=ProviderConfidence.INBOX_ONLY,
    inbox_url_template="https://mail.sina.com.cn/",
)

_ALIYUN = ProviderSpec(
    provider=WebmailProvider.ALIYUN,
    label="Aliyun Mail",
    confidence=ProviderConfidence.INBOX_ONLY,
    inbox_url_template="https://mail.aliyun.com/",
)

_NAVER = ProviderSpec(
    provider=WebmailProvider.NAVER,
    label="Naver Mail",
    confidence=ProviderConfidence.INBOX_ONLY,
    inbox_url_template="https://mail.naver.com/",
)

_DAUM = ProviderSpec(
    provider=WebmailProvider.DAUM,
    label="Daum Mail",
    confidence=ProviderConfidence.INBOX_ONLY,
    inbox_url_template="https://mail.daum.net/",
)

_WEB_DE = ProviderSpec(
    provider=WebmailProvider.WEB_DE,
    label="WEB.DE",
    confidence=ProviderConfidence.INBOX_ONLY,
    inbox_url_template="https://web.de/",
)

_TONLINE = ProviderSpec(
    provider=WebmailProvider.TONLINE,
    label="T-Online",
    confidence=ProviderConfidence.INBOX_ONLY,
    inbox_url_template="https://email.t-online.de/",
)

_SEZNAM = ProviderSpec(
    provider=WebmailProvider.SEZNAM,
    label="Seznam",
    confidence=ProviderConfidence.INBOX_ONLY,
    inbox_url_template="https://email.seznam.cz/",
)

_WP_PL = ProviderSpec(
    provider=WebmailProvider.WP_PL,
    label="WP Poczta",
    confidence=ProviderConfidence.INBOX_ONLY,
    inbox_url_template="https://poczta.wp.pl/",
)

_O2_PL = ProviderSpec(
    provider=WebmailProvider.O2_PL,
    label="o2 Poczta",
    confidence=ProviderConfidence.INBOX_ONLY,
    inbox_url_template="https://poczta.o2.pl/",
)

_INTERIA = ProviderSpec(
    provider=WebmailProvider.INTERIA,
    label="Interia Poczta",
    confidence=ProviderConfidence.INBOX_ONLY,
    inbox_url_template="https://poczta.interia.pl/",
)

_LIBERO = ProviderSpec(
    provider=WebmailProvider.LIBERO,
    label="Libero Mail",
    confidence=ProviderConfidence.INBOX_ONLY,
    inbox_url_template="https://webmail.libero.it/",
)

_VIRGILIO = ProviderSpec(
    provider=WebmailProvider.VIRGILIO,
    label="Virgilio Mail",
    confidence=ProviderConfidence.INBOX_ONLY,
    inbox_url_template="https://mail.virgilio.it/",
)

_ORANGE = ProviderSpec(
    provider=WebmailProvider.ORANGE,
    label="Orange Mail",
    confidence=ProviderConfidence.INBOX_ONLY,
    inbox_url_template="https://webmail.orange.fr/",
)

_LAPOSTE = ProviderSpec(
    provider=WebmailProvider.LAPOSTE,
    label="Laposte.net",
    confidence=ProviderConfidence.INBOX_ONLY,
    inbox_url_template="https://www.laposte.net/accueil",
)

_FREE_FR = ProviderSpec(
    provider=WebmailProvider.FREE_FR,
    label="Free Webmail",
    confidence=ProviderConfidence.INBOX_ONLY,
    inbox_url_template="https://webmail.free.fr/",
)

_SFR = ProviderSpec(
    provider=WebmailProvider.SFR,
    label="SFR Mail",
    confidence=ProviderConfidence.INBOX_ONLY,
    inbox_url_template="https://webmail.sfr.fr/",
)


# ---------------------------------------------------------------------------
# Domain → provider spec (exact match, lowercase)
# ---------------------------------------------------------------------------

DOMAIN_TO_PROVIDER: Dict[str, ProviderSpec] = {
    # Gmail
    "gmail.com": _GMAIL,
    "googlemail.com": _GMAIL,
    # Outlook / Microsoft
    "outlook.com": _OUTLOOK,
    "hotmail.com": _OUTLOOK,
    "hotmail.co.uk": _OUTLOOK,
    "live.com": _OUTLOOK,
    "live.co.uk": _OUTLOOK,
    "msn.com": _OUTLOOK,
    "passport.com": _OUTLOOK,
    # Yahoo
    "yahoo.com": _YAHOO,
    "ymail.com": _YAHOO,
    "rocketmail.com": _YAHOO,
    "yahoo.co.uk": _YAHOO,
    "yahoo.co.jp": _YAHOO,
    "yahoo.fr": _YAHOO,
    "yahoo.de": _YAHOO,
    "yahoo.ca": _YAHOO,
    "yahoo.com.br": _YAHOO,
    "yahoo.es": _YAHOO,
    "yahoo.it": _YAHOO,
    "yahoo.com.au": _YAHOO,
    "yahoo.co.in": _YAHOO,
    "yahoo.com.mx": _YAHOO,
    # iCloud
    "icloud.com": _ICLOUD,
    "me.com": _ICLOUD,
    "mac.com": _ICLOUD,
    # Proton
    "proton.me": _PROTON,
    "protonmail.com": _PROTON,
    "pm.me": _PROTON,
    # Zoho
    "zoho.com": _ZOHO,
    "zohomail.com": _ZOHO,
    "zoho.eu": _ZOHO,
    "zoho.in": _ZOHO,
    # AOL
    "aol.com": _AOL,
    "aim.com": _AOL,
    "love.com": _AOL,
    "games.com": _AOL,
    "wow.com": _AOL,
    "ygm.com": _AOL,
    # Fastmail
    "fastmail.com": _FASTMAIL,
    "fastmail.fm": _FASTMAIL,
    "fastmail.us": _FASTMAIL,
    "sent.com": _FASTMAIL,
    "pobox.com": _FASTMAIL,
    # GMX
    "gmx.com": _GMX,
    "gmx.net": _GMX,
    "gmx.de": _GMX,
    "gmx.at": _GMX,
    "gmx.ch": _GMX,
    "gmx.co.uk": _GMX,
    "gmx.fr": _GMX,
    "gmx.es": _GMX,
    # mail.com
    "mail.com": _MAILCOM,
    "email.com": _MAILCOM,
    "usa.com": _MAILCOM,
    "europe.com": _MAILCOM,
    "mail.ru": _MAIL_RU,
    "bk.ru": _MAIL_RU,
    "inbox.ru": _MAIL_RU,
    "list.ru": _MAIL_RU,
    "internet.ru": _MAIL_RU,
    "mail.ua": _MAIL_RU,
    "xmail.ru": _MAIL_RU,
    # Yandex
    "yandex.ru": _YANDEX,
    "yandex.com": _YANDEX,
    "ya.ru": _YANDEX,
    "yandex.by": _YANDEX,
    "yandex.kz": _YANDEX,
    "yandex.ua": _YANDEX,
    "yandex.com.tr": _YANDEX,
    # Rambler
    "rambler.ru": _RAMBLER,
    "lenta.ru": _RAMBLER,
    "autorambler.ru": _RAMBLER,
    "ro.ru": _RAMBLER,
    "myrambler.ru": _RAMBLER,
    "rambler.ua": _RAMBLER,
    # QQ
    "qq.com": _QQ,
    "foxmail.com": _QQ,
    "vip.qq.com": _QQ,
    # NetEase
    "163.com": _NETEASE,
    "126.com": _NETEASE,
    "yeah.net": _NETEASE,
    "188.com": _NETEASE,
    "vip.163.com": _NETEASE,
    "vip.126.com": _NETEASE,
    # Sina
    "sina.com": _SINA,
    "sina.cn": _SINA,
    "vip.sina.com": _SINA,
    # Aliyun
    "aliyun.com": _ALIYUN,
    # Naver
    "naver.com": _NAVER,
    # Daum
    "daum.net": _DAUM,
    "hanmail.net": _DAUM,
    # web.de
    "web.de": _WEB_DE,
    # T-Online
    "t-online.de": _TONLINE,
    "t-online.com": _TONLINE,
    "magenta.de": _TONLINE,
    # Seznam
    "seznam.cz": _SEZNAM,
    "email.cz": _SEZNAM,
    "post.cz": _SEZNAM,
    "centrum.cz": _SEZNAM,
    "atlas.cz": _SEZNAM,
    "stream.cz": _SEZNAM,
    "spoluzaci.cz": _SEZNAM,
    # wp.pl
    "wp.pl": _WP_PL,
    "poczta.wp.pl": _WP_PL,
    # o2.pl
    "o2.pl": _O2_PL,
    "tlen.pl": _O2_PL,
    "go2.pl": _O2_PL,
    # Interia
    "interia.pl": _INTERIA,
    "interia.eu": _INTERIA,
    "poczta.fm": _INTERIA,
    # Libero
    "libero.it": _LIBERO,
    "iol.it": _LIBERO,
    "inwind.it": _LIBERO,
    "blu.it": _LIBERO,
    # Virgilio
    "virgilio.it": _VIRGILIO,
    "alice.it": _VIRGILIO,
    "tin.it": _VIRGILIO,
    "tim.it": _VIRGILIO,
    # Orange
    "orange.fr": _ORANGE,
    "wanadoo.fr": _ORANGE,
    # Laposte
    "laposte.net": _LAPOSTE,
    # Free
    "free.fr": _FREE_FR,
    "aliceadsl.fr": _FREE_FR,
    # SFR
    "sfr.fr": _SFR,
    "neuf.fr": _SFR,
    "cegetel.net": _SFR,
    "numericable.fr": _SFR,
}
