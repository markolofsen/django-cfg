"""Send the welcome letter to an arbitrary address, for review.

Why a service and not just a management command: reviewing the letter must
exercise the **same** code that a real signup does. Every hand-rolled
"just send a test copy" reproduces the letter with a different sender, a
different locale, or a different template path, and then proves nothing —
which is exactly how a `site_name` that no context provided, and a `noreply`
display name, both survived review.

So this deliberately routes through ``AccountNotifications.send_welcome_email``
(hence the real ``DjangoEmailService``, the real from-name, the real Reply-To and
the real per-locale template resolution) and differs from a production send in
exactly one way: it does not touch ``welcome_email_sent_at``, so the same address
can be previewed repeatedly without deleting the user first.

Not a preview of *whether* a user would get mail — that is
``services.welcome.send_welcome_email`` and its one-per-user guard.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from .welcome import DEFAULT_LOCALE, SUPPORTED_LOCALES, resolve_locale

logger = logging.getLogger(__name__)


class UnsupportedLocale(ValueError):
    """Raised for a locale the platform ships no letter for."""


def send_welcome_preview(
    email: str,
    locale: Optional[str] = None,
    user: Optional[Any] = None,
) -> str:
    """Send the welcome letter to ``email``. Returns the locale used.

    ``locale`` may be any supported tag; omit it to resolve the way a real send
    would (the user's stored language, else the project default).

    ``user`` supplies the template context. Omit it and an unsaved stand-in is
    built from ``email`` — unsaved on purpose, so previewing cannot create an
    account or mutate an existing one.

    Raises ``UnsupportedLocale`` rather than quietly falling back to English: a
    typo in a locale tag would otherwise look like "the translation is missing",
    and someone would go looking for a file that is right there.
    """
    if locale:
        if locale not in SUPPORTED_LOCALES:
            raise UnsupportedLocale(
                f"{locale!r} is not in SUPPORTED_LOCALES ({', '.join(SUPPORTED_LOCALES)})"
            )
        resolved = locale
    elif user is not None:
        resolved = resolve_locale(user)
    else:
        resolved = DEFAULT_LOCALE

    if user is None:
        # Imported at call time: the app registry is not ready at import.
        from django.contrib.auth import get_user_model

        # Unsaved: never write to the database from a preview.
        user = get_user_model()(email=email, username=email.split("@")[0])

    # Imported here to mirror services.welcome and stay clear of the import cycle
    # between accounts.utils and accounts.services.
    from ..utils.notifications import AccountNotifications

    AccountNotifications.send_welcome_email(
        user=user, locale=resolved, send_email=True, send_telegram=False
    )
    logger.info("Welcome preview queued for %s (locale=%s)", email, resolved)
    return resolved
