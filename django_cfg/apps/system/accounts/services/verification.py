"""Shared email-verification hook.

The sticky ``is_email_verified`` flag and the ``user_email_verified`` signal
are the single extension point downstream products use to react to a proven
email — most notably to enroll the address into a marketing/newsletter list.

This lives at the ``services`` level (not inside ``otp_service``) so every
login path that proves an email — OTP verify AND OAuth, whose provider email
is already verified — can announce it the same way. The framework itself
stores no subscription; it only fires the signal with whatever ``consent``
evidence the caller captured (or ``None``).
"""

from __future__ import annotations

from typing import Optional

from django.utils import timezone

from ..models import CustomUser
from ..signals import user_email_verified


def mark_user_verified(user: CustomUser, consent: Optional[dict] = None) -> None:
    """Flip the sticky ``is_email_verified`` flag and announce the verification.

    The sticky flag flips only on the first proof; the ``user_email_verified``
    signal fires on *every* call so downstream consumers also see a consent
    granted at a later login. ``consent`` is the context captured by the caller
    (see the OTP ``_consent_context``) or ``None`` — e.g. an OAuth login whose
    provider email is already verified.
    """
    if not user.is_email_verified:
        user.is_email_verified = True
        user.email_verified_at = timezone.now()
        user.save(update_fields=["is_email_verified", "email_verified_at"])
    user_email_verified.send(sender=CustomUser, user=user, consent=consent)
