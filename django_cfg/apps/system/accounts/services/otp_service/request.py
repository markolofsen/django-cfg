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
from .types import OTPRequestResult

logger = get_logger(__name__)


@transaction.atomic
def request_otp(
    email: str,
    source_url: Optional[str] = None,
    accept_language: Optional[str] = None,
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

        # Save user language from Accept-Language (only if not already set)
        if accept_language and not user.language:
            lang_code = CustomUser.objects.clean_language(
                accept_language.split(",")[0].split(";")[0]
            )
            if lang_code:
                user.language = lang_code
                user.save(update_fields=["language"])

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
    else:
        # Invalidate old OTPs
        OTPSecret.objects.filter(email__iexact=cleaned_email, is_used=False).update(
            is_used=True
        )
        otp_code = OTPSecret.generate_otp()
        OTPSecret.objects.create(email=cleaned_email, secret=otp_code)
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

        if created and should_send_email:
            AccountNotifications.send_welcome_email(
                user=user, send_email=True, send_telegram=False,
            )

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
