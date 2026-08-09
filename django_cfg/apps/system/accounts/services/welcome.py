"""The one-time welcome letter.

Three things live here, and the split from the *content* of the letter is
deliberate: this module owns **when** a welcome is sent, **that it is sent only
once**, and **which locale** it renders in. What the letter actually says is the
product's business — it supplies
``templates/emails/welcome_email.<locale>.html`` and shadows the framework
default via app-directory template resolution.

Why the trigger is ``user_email_verified`` and not user creation:

- The previous implementation sent from ``request_otp``, gated on the
  ``register_user()`` ``created`` flag — i.e. at OTP *request*, before the
  address was proven. An address that never entered its code still got
  "welcome, your account has been created".
- It also missed OAuth entirely, since that path never called it. OAuth signups
  received no mail at all.

``mark_user_verified`` already announces both paths, so one receiver covers
both. But note it fires the signal on **every** verification and flips the
sticky ``is_email_verified`` flag only on the first — so the signal cannot be
the guard. ``welcome_email_sent_at`` is, claimed with a conditional UPDATE.
"""

from __future__ import annotations

import logging
from typing import Optional

from django.conf import settings
from django.utils import timezone

from ..models import CustomUser

logger = logging.getLogger(__name__)

# The locales the platform ships UI for. Mirrors the frontend SSoT,
# ``packages/i18n/src/locales/index.ts`` (re-exported as ``DEFAULT_LOCALES``
# from ``packages/nextjs/src/i18n/routing.ts``). Kept as an explicit list
# because the TS ``LocaleCode`` type is ``'en' | 'ru' | 'ko' | string`` and so
# constrains nothing — the file list is the real contract.
#
# ``pt-BR`` carries a region on purpose. There is no bare ``pt``, which is why
# ``resolve_locale`` must not blindly reduce a tag to two letters the way
# ``UserManager.clean_language`` does — that would map a Brazilian user to
# ``pt`` and match no template at all.
SUPPORTED_LOCALES: tuple[str, ...] = (
    "en", "ru", "ko", "ja", "de", "fr", "zh", "it", "es",
    "nl", "ar", "tr", "pt-BR", "pl", "sv", "no", "da",
)

DEFAULT_LOCALE = "en"

WELCOME_TEMPLATE = "emails/welcome"


def _match_supported(tag: str) -> Optional[str]:
    """Best supported locale for one BCP-47 tag, or None.

    Exact match wins (so ``pt-BR`` resolves to ``pt-BR``); otherwise the tag's
    base language is matched against both bare and region-carrying entries, so
    ``pt`` and ``pt-PT`` both reach ``pt-BR`` rather than falling back to
    English.
    """
    tag = (tag or "").strip().replace("_", "-")
    if not tag:
        return None

    lowered = tag.lower()
    by_lower = {loc.lower(): loc for loc in SUPPORTED_LOCALES}
    if lowered in by_lower:
        return by_lower[lowered]

    base = lowered.split("-")[0]
    if base in by_lower:
        return by_lower[base]
    for loc in SUPPORTED_LOCALES:
        if loc.lower().split("-")[0] == base:
            return loc
    return None


def parse_accept_language(header: str) -> list[str]:
    """Tags from an ``Accept-Language`` header, most-preferred first.

    Honors ``q`` weights; ``*`` is dropped. Django's own
    ``get_language_from_request`` is not used because it filters against
    ``settings.LANGUAGES``, which this package never populates.
    """
    tags: list[tuple[float, int, str]] = []
    for index, part in enumerate(header.split(",")):
        piece = part.strip()
        if not piece:
            continue
        tag, _, params = piece.partition(";")
        tag = tag.strip()
        if not tag or tag == "*":
            continue
        quality = 1.0
        for param in params.split(";"):
            key, _, value = param.partition("=")
            if key.strip() == "q":
                try:
                    quality = float(value)
                except ValueError:
                    quality = 0.0
        # index keeps the header's own order stable among equal weights
        tags.append((-quality, index, tag))
    return [tag for _, _, tag in sorted(tags)]


def persist_user_language(user: CustomUser, accept_language: str) -> None:
    """Store the user's language from ``Accept-Language``, once.

    Write-once (matching the OTP path): a later visit from a differently
    configured browser must not silently rewrite a preference the user may have
    set explicitly in their profile.

    Called from every path that proves an email. The OAuth path in particular
    used to persist nothing, so those users stayed ``language = ''`` forever and
    every localized email fell back to English.
    """
    if not accept_language or getattr(user, "language", ""):
        return

    for tag in parse_accept_language(accept_language):
        matched = _match_supported(tag)
        if matched:
            user.language = matched
            user.save(update_fields=["language"])
            return


def resolve_locale(user: CustomUser, accept_language: str = "") -> str:
    """The locale to render this user's email in.

    Order: the user's stored ``language`` → ``Accept-Language`` → the project's
    ``LANGUAGE_CODE`` → ``en``.

    ``Accept-Language`` matters more than it looks: the OAuth path persists no
    language at all, so for those users it is the only signal there is.
    """
    stored = getattr(user, "language", "") or ""
    if stored:
        matched = _match_supported(stored)
        if matched:
            return matched

    for tag in parse_accept_language(accept_language):
        matched = _match_supported(tag)
        if matched:
            return matched

    matched = _match_supported(getattr(settings, "LANGUAGE_CODE", "") or "")
    return matched or DEFAULT_LOCALE


def send_welcome_email(user: CustomUser, accept_language: str = "") -> bool:
    """Send the welcome letter, at most once per user.

    Returns True if this call sent it, False if it was already sent, the user is
    a test account, or the address is unusable.
    """
    if not user.email:
        return False
    if getattr(user, "is_test_account", False):
        logger.info("[TEST ACCOUNT] Skipping welcome email for %s", user.email)
        return False

    # Claim the send atomically. A read-then-write would let two concurrent
    # verifications both pass the check and mail the user twice.
    claimed = CustomUser.objects.filter(
        pk=user.pk, welcome_email_sent_at__isnull=True
    ).update(welcome_email_sent_at=timezone.now())
    if not claimed:
        return False

    locale = resolve_locale(user, accept_language)

    # Imported here: AccountNotifications imports this module's siblings, and a
    # module-level import would close the cycle.
    from ..utils.notifications import AccountNotifications

    try:
        AccountNotifications.send_welcome_email(
            user=user, locale=locale, send_email=True, send_telegram=False
        )
    except Exception:
        # Release the claim so a retry can still deliver. Sending itself is
        # threaded and fails asynchronously, so this only catches a synchronous
        # failure to *queue* — but leaving the stamp would silently cost the
        # user their only welcome.
        CustomUser.objects.filter(pk=user.pk).update(welcome_email_sent_at=None)
        logger.exception("Welcome email failed to queue for %s", user.email)
        raise

    logger.info("Welcome email queued for %s (locale=%s)", user.email, locale)
    return True
