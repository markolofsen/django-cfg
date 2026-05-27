"""OTP verify — validate code, mark used, flip ``is_email_verified``, log in.

Split out of the original monolithic ``otp_service.py`` so this critical
path is independently testable. Public entry point: ``OTPService.verify_otp``
(see service.py).

The ``is_email_verified`` hook (sticky flag flipped on the first
successful OTP) lives here — see ``_mark_user_verified``.
"""

from __future__ import annotations

from typing import Optional

from django.utils import timezone

from django_cfg.core.config import get_current_config
from django_cfg.modules.django_telegram import DjangoTelegram
from django_cfg.utils import get_logger

from ...models import CustomUser, OTPSecret
from ...signals import notify_failed_otp_attempt
from ..brute_force_service import OTPVerifyThrottle

logger = get_logger(__name__)


def _mark_user_verified(user: CustomUser) -> None:
    """Flip the sticky ``is_email_verified`` flag on first successful OTP."""
    if not user.is_email_verified:
        user.is_email_verified = True
        user.email_verified_at = timezone.now()
        user.save(update_fields=["is_email_verified", "email_verified_at"])


def _link_source(user: CustomUser, source_url: Optional[str]) -> None:
    if source_url:
        CustomUser.objects._link_user_to_source(user, source_url, is_new_user=False)


def verify_otp(
    email: str,
    otp_code: str,
    source_url: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> Optional[CustomUser]:
    """Verify OTP and return user if valid; ``None`` on any failure."""
    if not email or not otp_code:
        return None

    cleaned_email = CustomUser.objects.clean_email(email)
    cleaned_otp = otp_code.strip()
    if not cleaned_email or not cleaned_otp:
        return None

    # Check verify lockout
    locked, _ = OTPVerifyThrottle.is_locked(cleaned_email)
    if locked:
        logger.warning(f"OTP verify blocked - account locked: {cleaned_email}")
        notify_failed_otp_attempt(
            cleaned_email, ip_address=ip_address,
            reason="Account locked due to too many failed attempts",
        )
        return None

    # 1. Development mode bypass — accept any OTP
    dev_user = _try_dev_bypass(cleaned_email, source_url)
    if dev_user is not None:
        _mark_user_verified(dev_user)
        return dev_user

    # 2. Test account bypass — any OTP works for ``is_test_account=True`` users
    test_user = _try_test_account_bypass(cleaned_email, source_url, ip_address)
    if test_user is not None:
        _mark_user_verified(test_user)
        return test_user

    # 3. Normal validation against OTPSecret
    return _verify_real_otp(cleaned_email, cleaned_otp, source_url, ip_address)


def _try_dev_bypass(cleaned_email: str, source_url: Optional[str]) -> Optional[CustomUser]:
    try:
        config = get_current_config()
        logger.info(
            f"[OTP] Config retrieved: {config is not None}, "
            f"is_development: {config.is_development if config else 'N/A'}"
        )
        if not (config and config.is_development):
            return None

        logger.info(f"[DEV MODE] Bypassing OTP verification for {cleaned_email}")
        user = CustomUser.objects.filter(
            email__iexact=cleaned_email, deleted_at__isnull=True,
        ).first()

        # If email not found, fall back to first superuser (convenience login)
        if not user:
            logger.info(f"[DEV MODE] Email {cleaned_email} not found, using default account")
            user = (
                CustomUser.objects.filter(is_superuser=True).first()
                or CustomUser.objects.filter(is_active=True).first()
            )
        if not user:
            logger.error("[DEV MODE] No users found in database!")
            return None

        logger.info(f"[DEV MODE] Logging in as: {user.email} (superuser: {user.is_superuser})")
        _link_source(user, source_url)

        try:
            DjangoTelegram.send_info("Development OTP Login", {
                "Email (requested)": cleaned_email,
                "Email (actual)": user.email,
                "Username": user.username,
                "Source URL": source_url or "Direct",
                "Login Time": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "User ID": user.id,
                "Is Superuser": user.is_superuser,
                "Mode": "🔧 DEVELOPMENT (OTP Bypassed)",
            })
        except Exception as telegram_error:
            logger.error(f"Failed to send Telegram dev login notification: {telegram_error}")
        return user

    except Exception as e:
        logger.error(f"Error checking development mode: {e}")
        return None  # fall through to normal validation


def _try_test_account_bypass(
    cleaned_email: str, source_url: Optional[str], ip_address: Optional[str],
) -> Optional[CustomUser]:
    try:
        user = CustomUser.objects.filter(
            email__iexact=cleaned_email, deleted_at__isnull=True,
        ).first()

        if user and not user.is_active:
            logger.warning(f"[DELETED ACCOUNT] OTP attempt for deleted account: {cleaned_email}")
            notify_failed_otp_attempt(
                cleaned_email, ip_address=ip_address,
                reason="Account is deleted or deactivated",
            )
            return None

        if not (user and user.is_test_account):
            return None

        logger.info(f"[TEST ACCOUNT] OTP bypass for {cleaned_email}")
        _link_source(user, source_url)

        try:
            DjangoTelegram.send_warning("Test Account Login", {
                "Email": cleaned_email,
                "Username": user.username,
                "Source URL": source_url or "Direct",
                "Login Time": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "User ID": user.id,
                "Mode": "🧪 TEST ACCOUNT (OTP Bypassed)",
            })
        except Exception as telegram_error:
            logger.error(f"Failed to send Telegram test account notification: {telegram_error}")
        return user

    except Exception as e:
        logger.error(f"Error checking test account: {e}")
        return None


def _verify_real_otp(
    cleaned_email: str, cleaned_otp: str,
    source_url: Optional[str], ip_address: Optional[str],
) -> Optional[CustomUser]:
    try:
        otp_secret = OTPSecret.objects.filter(
            email__iexact=cleaned_email,
            secret=cleaned_otp,
            is_used=False,
            expires_at__gt=timezone.now(),
        ).first()

        if not otp_secret or not otp_secret.is_valid:
            logger.warning(f"Invalid OTP for {cleaned_email}")
            just_locked, _ = OTPVerifyThrottle.record_failure(cleaned_email)
            if just_locked:
                logger.warning(f"OTP brute-force lockout triggered for {cleaned_email}")
            try:
                notify_failed_otp_attempt(
                    cleaned_email, ip_address=ip_address,
                    reason="Invalid or expired OTP",
                )
            except Exception as e:
                logger.error(f"Failed to send failed OTP notification: {e}")
            return None

        otp_secret.mark_used()

        try:
            user = CustomUser.objects.filter(
                email__iexact=cleaned_email, deleted_at__isnull=True,
            ).first()

            if not user.is_active:
                logger.warning(
                    f"[DELETED ACCOUNT] OTP verified but account is deleted: {cleaned_email}"
                )
                notify_failed_otp_attempt(
                    cleaned_email, ip_address=ip_address,
                    reason="Account is deleted or deactivated",
                )
                return None

            _mark_user_verified(user)
            _link_source(user, source_url)

            try:
                DjangoTelegram.send_success("Successful OTP Login", {
                    "Email": cleaned_email,
                    "Username": user.username,
                    "Source URL": source_url or "Direct",
                    "Login Time": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "User ID": user.id,
                })
                logger.info(f"Telegram OTP verification notification sent for {cleaned_email}")
            except ImportError:
                logger.warning(
                    "django_cfg DjangoTelegram not available for OTP verification notifications"
                )
            except Exception as telegram_error:
                logger.error(
                    f"Failed to send Telegram OTP verification notification: {telegram_error}"
                )

            OTPVerifyThrottle.record_success(cleaned_email)
            logger.info(f"OTP verified for {cleaned_email}")
            return user

        except CustomUser.DoesNotExist:
            logger.warning(f"User was deleted after OTP was sent: {cleaned_email}")
            return None

    except Exception as e:
        logger.error(f"Error verifying OTP: {e}")
        return None
