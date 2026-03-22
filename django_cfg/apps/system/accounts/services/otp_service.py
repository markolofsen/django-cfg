import traceback
from dataclasses import dataclass
from typing import Optional

from django.db import transaction
from django.utils import timezone


@dataclass
class OTPRequestResult:
    """Result of an OTP send attempt."""
    success: bool
    error_code: str = ""        # 'ok' | 'invalid_email' | 'cooldown' | 'hourly_limit' | 'daily_limit' | 'user_creation_failed' | 'email_send_failed'
    retry_after: int = 0        # seconds until retry is allowed (0 = no restriction)

from django_cfg.core.utils import get_otp_url
from django_cfg.core.config import get_current_config
from django_cfg.modules.django_telegram import DjangoTelegram
from django_cfg.utils import get_logger

from ..models import CustomUser, OTPSecret
from ..signals import notify_failed_otp_attempt
from ..utils.notifications import AccountNotifications
from .brute_force_service import OTPRequestThrottle, OTPVerifyThrottle
from .email_validator import EmailValidationError, validate_email_address

logger = get_logger(__name__)


class OTPService:
    """Simple OTP service for authentication."""

    # Expose get_otp_url as a static method for backward compatibility
    _get_otp_url = staticmethod(get_otp_url)

    @staticmethod
    @transaction.atomic
    def request_otp(email: str, source_url: Optional[str] = None, accept_language: Optional[str] = None) -> OTPRequestResult:
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
                    accept_language.split(',')[0].split(';')[0]
                )
                if lang_code:
                    user.language = lang_code
                    user.save(update_fields=['language'])

        except Exception as e:
            logger.error(
                f"Error creating/finding user for email {cleaned_email}: {str(e)}"
            )
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return OTPRequestResult(success=False, error_code="user_creation_failed")

        # Check for existing active OTP
        existing_otp = OTPSecret.objects.filter(
            email__iexact=cleaned_email, is_used=False, expires_at__gt=timezone.now()
        ).first()

        if existing_otp and existing_otp.is_valid:
            otp_code = existing_otp.secret
            logger.info(f"Reusing active OTP for {cleaned_email}")
        else:
            # Invalidate old OTPs
            OTPSecret.objects.filter(email__iexact=cleaned_email, is_used=False).update(
                is_used=True
            )

            # Generate new OTP
            otp_code = OTPSecret.generate_otp()
            OTPSecret.objects.create(email=cleaned_email, secret=otp_code)
            logger.info(f"Generated new OTP for {cleaned_email}")

        # Send email using AccountNotifications
        try:
            # Skip email for test accounts (any OTP is accepted anyway)
            should_send_email = not user.is_test_account

            if user.is_test_account:
                logger.info(f"[TEST ACCOUNT] Skipping OTP email for {cleaned_email}")

            # Send OTP notification
            AccountNotifications.send_otp_notification(
                user=user,
                otp_code=otp_code,
                is_new_user=created,
                source_url=source_url,
                send_email=should_send_email,
                send_telegram=False  # Telegram notification sent separately below
            )

            # Send welcome email for new users (skip for test accounts)
            if created and should_send_email:
                AccountNotifications.send_welcome_email(
                    user=user,
                    send_email=True,
                    send_telegram=False
                )

            # Send Telegram notification for OTP request
            try:
                # Prepare notification data
                notification_data = {
                    "Email": cleaned_email,
                    "User Type": "New User" if created else "Existing User",
                    "OTP Code": otp_code,
                    "Source URL": source_url or "Direct",
                    "Timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC")
                }

                # Add test account indicator
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
                # Don't fail the OTP process if Telegram fails

            OTPRequestThrottle.record_sent(cleaned_email)
            return OTPRequestResult(success=True)
        except Exception as e:
            logger.error(f"Failed to send OTP email: {e}")
            return OTPRequestResult(success=False, error_code="email_send_failed")

    @staticmethod
    def verify_otp(
        email: str, otp_code: str, source_url: Optional[str] = None, ip_address: Optional[str] = None
    ) -> Optional[CustomUser]:
        """Verify OTP and return user if valid."""
        print(f"[OTP PRINT TEST] verify_otp called for email: {email}")
        logger.info(f"[OTP TEST] verify_otp called for email: {email}")

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
            notify_failed_otp_attempt(cleaned_email, ip_address=ip_address, reason="Account locked due to too many failed attempts")
            return None

        # Development mode bypass - accept any OTP
        try:
            config = get_current_config()
            logger.info(f"[OTP] Config retrieved: {config is not None}, is_development: {config.is_development if config else 'N/A'}")
            if config and config.is_development:
                logger.info(f"[DEV MODE] Bypassing OTP verification for {cleaned_email}")

                # Try to find active user by email first (allows testing specific accounts)
                user = CustomUser.objects.filter(email__iexact=cleaned_email, deleted_at__isnull=True).first()

                # If email not found, use first superuser or regular user (convenience login)
                if not user:
                    logger.info(f"[DEV MODE] Email {cleaned_email} not found, using default account")
                    user = CustomUser.objects.filter(is_superuser=True).first()
                    if not user:
                        user = CustomUser.objects.filter(is_active=True).first()

                if not user:
                    logger.error(f"[DEV MODE] No users found in database!")
                    return None

                logger.info(f"[DEV MODE] Logging in as: {user.email} (superuser: {user.is_superuser})")

                # Link user to source if provided
                if source_url:
                    CustomUser.objects._link_user_to_source(
                        user, source_url, is_new_user=False
                    )

                # Send Telegram notification for development login
                try:
                    verification_data = {
                        "Email (requested)": cleaned_email,
                        "Email (actual)": user.email,
                        "Username": user.username,
                        "Source URL": source_url or "Direct",
                        "Login Time": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                        "User ID": user.id,
                        "Is Superuser": user.is_superuser,
                        "Mode": "🔧 DEVELOPMENT (OTP Bypassed)"
                    }
                    DjangoTelegram.send_info("Development OTP Login", verification_data)
                except Exception as telegram_error:
                    logger.error(f"Failed to send Telegram dev login notification: {telegram_error}")

                return user

        except Exception as e:
            logger.error(f"Error checking development mode: {e}")
            # Fall through to normal OTP validation

        # Test account bypass (for App Store review, API testing, etc.)
        # If user is marked as test account, accept any OTP code
        try:
            user = CustomUser.objects.filter(email__iexact=cleaned_email, deleted_at__isnull=True).first()

            # Check if user is deleted/deactivated
            if user and not user.is_active:
                logger.warning(f"[DELETED ACCOUNT] OTP attempt for deleted account: {cleaned_email}")
                notify_failed_otp_attempt(cleaned_email, ip_address=ip_address, reason="Account is deleted or deactivated")
                return None

            if user and user.is_test_account:
                logger.info(f"[TEST ACCOUNT] OTP bypass for {cleaned_email}")

                # Link user to source if provided
                if source_url:
                    CustomUser.objects._link_user_to_source(
                        user, source_url, is_new_user=False
                    )

                # Send Telegram notification for test account login
                try:
                    verification_data = {
                        "Email": cleaned_email,
                        "Username": user.username,
                        "Source URL": source_url or "Direct",
                        "Login Time": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                        "User ID": user.id,
                        "Mode": "🧪 TEST ACCOUNT (OTP Bypassed)"
                    }
                    DjangoTelegram.send_warning("Test Account Login", verification_data)
                except Exception as telegram_error:
                    logger.error(f"Failed to send Telegram test account notification: {telegram_error}")

                return user

        except Exception as e:
            logger.error(f"Error checking test account: {e}")
            # Fall through to normal OTP validation

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

                # Send Telegram notification for failed OTP attempt
                try:
                    notify_failed_otp_attempt(cleaned_email, ip_address=ip_address, reason="Invalid or expired OTP")
                except Exception as e:
                    logger.error(f"Failed to send failed OTP notification: {e}")

                return None

            # Mark OTP as used
            otp_secret.mark_used()

            # Get active user
            try:
                user = CustomUser.objects.filter(email__iexact=cleaned_email, deleted_at__isnull=True).first()

                # Check if user is deleted/deactivated
                if not user.is_active:
                    logger.warning(f"[DELETED ACCOUNT] OTP verified but account is deleted: {cleaned_email}")
                    notify_failed_otp_attempt(cleaned_email, ip_address=ip_address, reason="Account is deleted or deactivated")
                    return None

                # Link user to source if provided (for existing users logging in from new sources)
                if source_url:
                    CustomUser.objects._link_user_to_source(
                        user, source_url, is_new_user=False
                    )

                # Send Telegram notification for successful OTP verification
                try:

                    verification_data = {
                        "Email": cleaned_email,
                        "Username": user.username,
                        "Source URL": source_url or "Direct",
                        "Login Time": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                        "User ID": user.id
                    }

                    DjangoTelegram.send_success("Successful OTP Login", verification_data)
                    logger.info(f"Telegram OTP verification notification sent for {cleaned_email}")

                except ImportError:
                    logger.warning("django_cfg DjangoTelegram not available for OTP verification notifications")
                except Exception as telegram_error:
                    logger.error(f"Failed to send Telegram OTP verification notification: {telegram_error}")

                OTPVerifyThrottle.record_success(cleaned_email)
                logger.info(f"OTP verified for {cleaned_email}")
                return user
            except CustomUser.DoesNotExist:
                # User was deleted after OTP was sent
                logger.warning(f"User was deleted after OTP was sent: {cleaned_email}")
                return None

        except Exception as e:
            logger.error(f"Error verifying OTP: {e}")
            return None
