"""The one-time welcome letter.

Three things live here, and the split from the *content* of the letter is
deliberate: this module owns **when** a welcome is sent, **that it is sent only
once**, and **which locale** it renders in. What the letter actually says lives
in the mailer app: ``EmailContent`` rows per locale, rendered by the product's
own ``templates/emails/welcome/_shell.html``. The locale *policy* — which
languages exist, how a header is parsed — is ``mailer.locales``.

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

from django.utils import timezone

from ..models import CustomUser

logger = logging.getLogger(__name__)

# Locale policy lives in the mailer app: which languages the platform can write
# a letter in is a mail concern, not a property of the accounts feature. Kept as
# re-exports so existing imports of these names keep working.
from django_cfg.apps.system.mailer.locales import (  # noqa: E402
    DEFAULT_LOCALE,
    SUPPORTED_LOCALES,
    best_supported,
    match_supported as _match_supported,
    parse_accept_language,
)

WELCOME_TEMPLATE = "emails/welcome"


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

    matched = best_supported(accept_language)
    if matched:
        user.language = matched
        user.save(update_fields=["language"])


def resolve_locale(user: CustomUser, accept_language: str = "") -> str:
    """The locale to render this user's email in.

    Order: the user's stored ``language`` → ``Accept-Language`` → ``en``.

    ``settings.LANGUAGE_CODE`` is deliberately NOT in that chain. It is the
    project's own default, not a statement about this reader: on a project
    configured as ``ru`` it would send a Russian letter to a French speaker whose
    language we do not ship, which is worse than English — the one language a
    recipient of an English-language product is most likely to read.
    """
    stored = getattr(user, "language", "") or ""
    if stored:
        matched = _match_supported(stored)
        if matched:
            return matched

    return best_supported(accept_language) or DEFAULT_LOCALE


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
