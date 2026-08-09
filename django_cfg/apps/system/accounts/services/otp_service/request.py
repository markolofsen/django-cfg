"""OTP request — generate a code, persist it, send the email + notifications.

Split out of the original monolithic ``otp_service.py`` so the request
and verify paths can be tested and iterated on independently. Public
entry point: ``OTPService.request_otp`` (see service.py).
"""

from __future__ import annotations

import traceback
from typing import Optional

from django.db import transaction
from django.utils import timezone

from django_cfg.modules.django_telegram import DjangoTelegram
from django_cfg.utils import get_logger

from ...models import CustomUser, OTPSecret
from ...utils.notifications import AccountNotifications
from ..brute_force_service import OTPRequestThrottle
from ..email_validator import EmailValidationError, validate_email_address
from .types import ConsentCapture, OTPRequestResult

logger = get_logger(__name__)


@transaction.atomic
def request_otp(
    email: str,
    source_url: Optional[str] = None,
    accept_language: Optional[str] = None,
    consent: Optional[ConsentCapture] = None,
) -> OTPRequestResult:
    """Generate and send OTP to email. Returns OTPRequestResult."""
    cleaned_email = CustomUser.objects.clean_email(email)
    if not cleaned_email:
        return OTPRequestResult(success=False, error_code="invalid_email")

    # Deep email validation: syntax + disposable blocklist + MX check.
    try:
        cleaned_email = validate_email_address(cleaned_email)
    except EmailValidationError as exc:
        logger.info(f"OTP request rejected — invalid email {cleaned_email!r}: {exc}")
        return OTPRequestResult(success=False, error_code=exc.error_code)

    # Check send throttle
    allowed, reason, retry_after = OTPRequestThrottle.check_email(cleaned_email)
    if not allowed:
        logger.info(f"OTP request throttled for {cleaned_email}: {reason}, retry in {retry_after}s")
        return OTPRequestResult(success=False, error_code=reason, retry_after=retry_after)

    # Find or create user using the manager's register_user method
    try:
        logger.info(f"Attempting to register user for email: {cleaned_email}")
        user, created = CustomUser.objects.register_user(
            cleaned_email, source_url=source_url
        )

        if created:
            logger.info(f"Created new user: {cleaned_email}")

        # Save the user's language from Accept-Language, once.
        #
        # This used to take the header's FIRST tag and reduce it to two letters,
        # which is wrong in three ways that all reach a real inbox:
        #   `de;q=0.7,ru,en;q=0.9` stored `de` although `ru` is the preferred one
        #   (an unweighted tag is q=1.0); `pt-BR,...` stored `pt`, for which no
        #   template or copy exists; and `xx-YY,de` stored the nonexistent `xx`.
        # `persist_user_language` honours q-weights and only stores a tag the
        # platform actually ships, so there is one parser instead of two that
        # disagree.
        if accept_language:
            from ..welcome import persist_user_language

            persist_user_language(user, accept_language)

    except Exception as e:
        logger.error(
            f"Error creating/finding user for email {cleaned_email}: {str(e)}"
        )
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return OTPRequestResult(success=False, error_code="user_creation_failed")

    # Reuse an existing valid OTP, otherwise generate a new one
    existing_otp = OTPSecret.objects.filter(
        email__iexact=cleaned_email, is_used=False, expires_at__gt=timezone.now(),
    ).first()

    if existing_otp and existing_otp.is_valid:
        otp_code = existing_otp.secret
        logger.info(f"Reusing active OTP for {cleaned_email}")
        # Latest explicit consent choice wins; a consent-less resend keeps it.
        if consent and consent.marketing_consent is not None:
            existing_otp.marketing_consent = consent.marketing_consent
            existing_otp.consent_disclosure_version = consent.disclosure_version
            existing_otp.consent_jurisdiction_hint = consent.jurisdiction_hint
            existing_otp.save(update_fields=[
                "marketing_consent", "consent_disclosure_version", "consent_jurisdiction_hint",
            ])
    else:
        # Invalidate old OTPs
        OTPSecret.objects.filter(email__iexact=cleaned_email, is_used=False).update(
            is_used=True
        )
        otp_code = OTPSecret.generate_otp()
        OTPSecret.objects.create(
            email=cleaned_email,
            secret=otp_code,
            marketing_consent=consent.marketing_consent if consent else None,
            consent_disclosure_version=consent.disclosure_version if consent else "",
            consent_jurisdiction_hint=consent.jurisdiction_hint if consent else "",
        )
        logger.info(f"Generated new OTP for {cleaned_email}")

    # Send email using AccountNotifications
    try:
        should_send_email = not user.is_test_account
        if user.is_test_account:
            logger.info(f"[TEST ACCOUNT] Skipping OTP email for {cleaned_email}")

        AccountNotifications.send_otp_notification(
            user=user,
            otp_code=otp_code,
            is_new_user=created,
            source_url=source_url,
            send_email=should_send_email,
            send_telegram=False,  # sent separately below
        )

        # No welcome email here: this is OTP *request*, so the address is not
        # proven yet and OAuth signups never reach this code at all. The welcome
        # letter is sent from the ``user_email_verified`` receiver instead —
        # see ``services/welcome.py``.

        # Telegram operator notification for the request
        try:
            notification_data = {
                "Email": cleaned_email,
                "User Type": "New User" if created else "Existing User",
                "OTP Code": otp_code,
                "Source URL": source_url or "Direct",
                "Timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            }
            if user.is_test_account:
                notification_data["Mode"] = "🧪 TEST ACCOUNT (Email skipped)"

            if created:
                DjangoTelegram.send_success("New User OTP Request", notification_data)
            elif user.is_test_account:
                DjangoTelegram.send_warning("Test Account OTP Request", notification_data)
            else:
                DjangoTelegram.send_info("OTP Login Request", notification_data)

            logger.info(f"Telegram OTP notification sent for {cleaned_email}")
        except ImportError:
            logger.warning("django_cfg DjangoTelegram not available for OTP notifications")
        except Exception as telegram_error:
            logger.error(f"Failed to send Telegram OTP notification: {telegram_error}")

        OTPRequestThrottle.record_sent(cleaned_email)
        return OTPRequestResult(success=True)

    except Exception as e:
        logger.error(f"Failed to send OTP email: {e}")
        return OTPRequestResult(success=False, error_code="email_send_failed")
