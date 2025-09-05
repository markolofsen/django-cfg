import logging
import traceback
from django.utils import timezone
from django.db import transaction
from typing import Optional

from django_cfg.modules.django_telegram import DjangoTelegram
from ..models import OTPSecret, CustomUser
from ..utils.auth_email_service import AuthEmailService
from ..signals import notify_failed_otp_attempt

logger = logging.getLogger(__name__)


class OTPService:
    """Simple OTP service for authentication."""

    @staticmethod
    def _get_otp_url(otp_code: str) -> str:
        """Get OTP verification URL from configuration."""
        try:
            from django_cfg.core.config import get_current_config
            config = get_current_config()
            if config and hasattr(config, 'get_otp_url'):
                return config.get_otp_url(otp_code)
            else:
                # Fallback URL if config is not available
                return f"#otp-{otp_code}"
        except Exception as e:
            logger.warning(f"Could not generate OTP URL: {e}")
            return f"#otp-{otp_code}"

    @staticmethod
    @transaction.atomic
    def request_otp(email: str, source_url: Optional[str] = None) -> tuple[bool, str]:
        """Generate and send OTP to email. Returns (success, error_type)."""
        cleaned_email = email.strip().lower()
        if not cleaned_email:
            return False, "invalid_email"

        # Find or create user using the manager's register_user method
        try:
            logger.info(f"Attempting to register user for email: {cleaned_email}")
            user, created = CustomUser.objects.register_user(
                cleaned_email, source_url=source_url
            )

            if created:
                logger.info(f"Created new user: {cleaned_email}")

        except Exception as e:
            logger.error(
                f"Error creating/finding user for email {cleaned_email}: {str(e)}"
            )
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return False, "user_creation_failed"

        # Check for existing active OTP
        existing_otp = OTPSecret.objects.filter(
            email=cleaned_email, is_used=False, expires_at__gt=timezone.now()
        ).first()

        if existing_otp and existing_otp.is_valid:
            otp_code = existing_otp.secret
            logger.info(f"Reusing active OTP for {cleaned_email}")
        else:
            # Invalidate old OTPs
            OTPSecret.objects.filter(email=cleaned_email, is_used=False).update(
                is_used=True
            )

            # Generate new OTP
            otp_code = OTPSecret.generate_otp()
            OTPSecret.objects.create(email=cleaned_email, secret=otp_code)
            logger.info(f"Generated new OTP for {cleaned_email}")

        # Send email using AuthEmailService
        try:
            # Generate OTP link

            otp_link = OTPService._get_otp_url(otp_code)

            # Send OTP email
            email_service = AuthEmailService(user)
            email_service.send_otp_email(otp_code, otp_link)

            # Send welcome email for new users
            if created:
                email_service.send_welcome_email(user.username)

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
                
                if created:
                    DjangoTelegram.send_success("New User OTP Request", notification_data)
                else:
                    DjangoTelegram.send_info("OTP Login Request", notification_data)
                    
                logger.info(f"Telegram OTP notification sent for {cleaned_email}")
                
            except ImportError:
                logger.warning("django_cfg DjangoTelegram not available for OTP notifications")
            except Exception as telegram_error:
                logger.error(f"Failed to send Telegram OTP notification: {telegram_error}")
                # Don't fail the OTP process if Telegram fails

            return True, "success"
        except Exception as e:
            logger.error(f"Failed to send OTP email: {e}")
            return False, "email_send_failed"

    @staticmethod
    def verify_otp(
        email: str, otp_code: str, source_url: Optional[str] = None
    ) -> Optional[CustomUser]:
        """Verify OTP and return user if valid."""
        if not email or not otp_code:
            return None

        cleaned_email = email.strip().lower()
        cleaned_otp = otp_code.strip()

        if not cleaned_email or not cleaned_otp:
            return None

        try:
            otp_secret = OTPSecret.objects.filter(
                email=cleaned_email,
                secret=cleaned_otp,
                is_used=False,
                expires_at__gt=timezone.now(),
            ).first()

            if not otp_secret or not otp_secret.is_valid:
                logger.warning(f"Invalid OTP for {cleaned_email}")
                
                # Send Telegram notification for failed OTP attempt
                try:
                    notify_failed_otp_attempt(cleaned_email, reason="Invalid or expired OTP")
                except Exception as e:
                    logger.error(f"Failed to send failed OTP notification: {e}")
                
                return None

            # Mark OTP as used
            otp_secret.mark_used()

            # Get user
            try:
                user = CustomUser.objects.get(email=cleaned_email)

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

                logger.info(f"OTP verified for {cleaned_email}")
                return user
            except CustomUser.DoesNotExist:
                # User was deleted after OTP was sent
                logger.warning(f"User was deleted after OTP was sent: {cleaned_email}")
                return None

        except Exception as e:
            logger.error(f"Error verifying OTP: {e}")
            return None
