"""
User Account Notification System
Centralized email and telegram notifications for user account events
"""
import logging

from django.utils import timezone

from django_cfg.core.state import get_current_config
from django_cfg.modules.django_email import DjangoEmailService
from django_cfg.modules.django_email.service import text_direction
from django_cfg.modules.django_telegram import DjangoTelegram

# Get config once
config = get_current_config()
logger = logging.getLogger(__name__)


def _resolve_copy(template_name: str, locale: str = None) -> dict:
    """Database copy for a letter, as template context, or ``{}``.

    The key is the template's own directory (``emails/welcome`` -> ``welcome``),
    so a project stores copy under the name it already uses for the template
    instead of maintaining a second mapping that can disagree.

    Failure is never fatal: before the table's migration has run, or on any
    database error, a letter must still go out with its built-in wording rather
    than not at all.
    """
    key = (template_name or "").rstrip("/").split("/")[-1]
    if not key:
        return {}
    try:
        from django_cfg.apps.system.mailer.models import EmailContent

        row = EmailContent.resolve(key, locale or "")
        return row.as_context() if row else {}
    except Exception as e:  # table missing, db down — not worth losing the mail
        logger.debug("Email copy lookup skipped for %r: %s", key, e)
        return {}


class AccountNotifications:
    """Centralized account notification system"""

    # === PRIVATE EMAIL METHODS ===

    @staticmethod
    def _send_email(
        user,
        subject: str,
        main_text: str,
        main_html_content: str,
        secondary_text: str,
        button_text: str,
        button_url: str = None,
        template_name: str = "emails/base_email",
        locale: str = None,
        extra_context: dict = None,
        text_only: bool = False,
    ):
        """Private method for sending templated emails."""
        email_service = DjangoEmailService()

        # Prepare context for template
        context = {
            "user": user,
            "subject": subject,
            "main_text": main_text,
            "main_html_content": main_html_content,
            "secondary_text": secondary_text,
            "button_text": button_text,
            "button_url": button_url,
            # Derived here, not in each template: a translator who adds an RTL
            # locale should not also have to remember to set the direction.
            "text_dir": text_direction(locale),
            # Editable per-locale copy, when this project loaded any. Absent is
            # normal and not an error: the template's own wording is the
            # fallback, so a fresh install still sends a correct letter.
            "copy": _resolve_copy(template_name, locale),
        }
        if extra_context:
            context.update(extra_context)

        email_service.send_template(
            subject=subject,
            template_name=template_name,
            context=context,
            recipient_list=[user.email],
            locale=locale,
            text_only=text_only,
        )

    # === EMAIL NOTIFICATIONS ===

    @staticmethod
    def send_welcome_email(
        user, locale=None, send_email=True, send_telegram=True, text_only=True
    ):
        """Send welcome email and telegram notification for new user.

        Renders ``emails/welcome`` — a template a product is expected to
        override per locale (``emails/welcome/<locale>.html``). The inline
        ``main_*`` strings below are only the fallback the framework's own
        default template uses; a product template ignores them and writes its
        own copy.

        Prefer ``services.welcome.send_welcome_email``, which resolves the
        locale and guarantees one send per user. Calling this directly sends
        unconditionally.
        """
        if send_email:
            AccountNotifications._send_email(
                user=user,
                subject=f"Welcome to {config.project_name}",
                main_text=f"Welcome {user.username}! Your account has been successfully created.",
                main_html_content=f'<p style="font-size: 1.5em; font-weight: bold; color: #28a745;">Welcome {user.username}!</p>',
                secondary_text="You can now access all our services and start exploring our API.",
                button_text=f"Go to {config.project_name}",
                button_url=config.site_url,
                template_name="emails/welcome",
                locale=locale,
                # Plain text by default: this letter is written in the first
                # person and asks for a reply, and an HTML page imitating a typed
                # message reads as marketing however carefully it is styled.
                text_only=text_only,
            )
            logger.info(f"Welcome email sent to {user.email}")

        if send_telegram:
            DjangoTelegram.send_success(
                "👤 New User Registered!",
                {
                    "email": user.email,
                    "username": user.username,
                    "date_joined": user.date_joined.strftime("%Y-%m-%d %H:%M"),
                    "is_active": user.is_active,
                    "is_staff": user.is_staff
                }
            )
            logger.info(f"Welcome telegram notification sent for {user.email}")

    @staticmethod
    def send_profile_update_notification(user, changes, send_email=True, send_telegram=True):
        """Send profile update notification"""
        if not changes:
            return

        change_text = ", ".join(changes)

        if send_email:
            AccountNotifications._send_email(
                user=user,
                subject="Security Alert: Profile Updated ⚠️",
                main_text="A security alert has been triggered for your account.",
                main_html_content='<p style="font-size: 1.5em; font-weight: bold; color: #dc3545;">Profile Updated</p>',
                secondary_text=f"Details: Your {change_text} has been updated. If this wasn't you, please contact support immediately.",
                button_text="Review Account",
            )
            logger.info(f"Profile update notification sent to {user.email}")

        if send_telegram:
            DjangoTelegram.send_warning(
                "👤 User Profile Updated",
                {
                    "user": user.email,
                    "changes": change_text,
                    "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "user_id": user.id
                }
            )
            logger.info(f"Profile update telegram notification sent for {user.email}")

    @staticmethod
    def send_account_status_change(user, status_type, reason=None, send_email=True, send_telegram=True):
        """Send account status change notification (activated/deactivated)"""
        if send_email:
            if status_type == "activated":
                AccountNotifications._send_email(
                    user=user,
                    subject=f"Account Activated - {config.project_name} ✅",
                    main_text="Your account has been activated and is now ready to use!",
                    main_html_content='<p style="font-size: 1.5em; font-weight: bold; color: #28a745;">Account Activated!</p>',
                    secondary_text="You now have full access to all our services and features.",
                    button_text="Access Private",
                    button_url=f"{config.site_url}/private",
                )
                logger.info(f"Account activation email sent to {user.email}")

            elif status_type == "deactivated":
                AccountNotifications._send_email(
                    user=user,
                    subject=f"Account Status Update - {config.project_name} ⚠️",
                    main_text="Your account status has been updated.",
                    main_html_content='<p style="font-size: 1.5em; font-weight: bold; color: #dc3545;">Account Deactivated</p>',
                    secondary_text=f"Reason: {reason or 'Account deactivated by administrator'}\nIf you believe this is an error, please contact our support team.",
                    button_text="Contact Support",
                )
                logger.info(f"Account deactivation email sent to {user.email}")

        if send_telegram:
            emoji = "✅" if status_type == "activated" else "❌"
            title = f"{emoji} Account {status_type.title()}"

            data = {
                "user": user.email,
                "status": status_type,
                "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "user_id": user.id
            }

            if reason:
                data["reason"] = reason

            if status_type == "activated":
                DjangoTelegram.send_success(title, data)
            else:
                DjangoTelegram.send_warning(title, data)

            logger.info(f"Account status change telegram notification sent for {user.email}")

    @staticmethod
    def send_login_notification(user, ip_address=None, send_email=False, send_telegram=True):
        """Send login notification (usually only telegram for security monitoring)"""
        if send_email:
            login_time = timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            ip_text = f" from IP address {ip_address}" if ip_address else ""
            AccountNotifications._send_email(
                user=user,
                subject=f"Login Notification - {config.project_name} 🔐",
                main_text=f"We detected a login to your account at {login_time}{ip_text}.",
                main_html_content=f'<p style="font-size: 1.2em; color: #007bff;">Login at {login_time}</p>',
                secondary_text="If this wasn't you, please secure your account immediately and contact support.",
                button_text="Review Account Security",
            )
            logger.info(f"Login notification email sent to {user.email}")

        if send_telegram:
            DjangoTelegram.send_info(
                "🔐 User Login",
                {
                    "user": user.email,
                    "username": user.username,
                    "login_time": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "ip_address": ip_address or "Unknown",
                    "user_id": user.id
                }
            )
            logger.info(f"Login telegram notification sent for {user.email}")

    @staticmethod
    def send_otp_notification(user, otp_code, is_new_user=False, source_url=None, send_email=True, send_telegram=True):
        """Send OTP notification via email"""
        if send_email:
            from ..services.otp_service import OTPService
            otp_link = OTPService._get_otp_url(otp_code, email=user.email)
            AccountNotifications._send_email(
                user=user,
                # The code is deliberately NOT in the subject. A subject line is
                # rendered by every lock-screen notification, mail-app preview
                # pane and IMAP sync log — surfaces that show it without the
                # recipient unlocking anything, and that a shoulder-surfer or a
                # synced second device sees for free. The body below carries the
                # code, which requires opening the message. Same reasoning as
                # `communications-and-notifications.md:44-48` (action links must
                # survive link-preview consumption): a secret must not be
                # readable from a preview of the thing that carries it.
                subject="Your sign-in code",
                main_text="Use the code below or click the button to authenticate:",
                main_html_content=f'<p style="font-size: 2em; font-weight: bold; color: #007bff;">{otp_code}</p>',
                secondary_text="This code expires in 10 minutes.",
                button_text="Login with OTP",
                button_url=otp_link,
            )
            logger.info(f"OTP email sent to {user.email}")

        if send_telegram:
            notification_data = {
                "email": user.email,
                "user_type": "New User" if is_new_user else "Existing User",
                "otp_code": otp_code,
                "source_url": source_url or "Direct",
                "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            }

            if is_new_user:
                DjangoTelegram.send_success("🆕 New User OTP Request", notification_data)
            else:
                DjangoTelegram.send_info("🔑 OTP Login Request", notification_data)

            logger.info(f"OTP telegram notification sent for {user.email}")

    @staticmethod
    def send_otp_verification_success(user, source_url=None, send_telegram=True):
        """Send successful OTP verification notification"""
        if send_telegram:
            verification_data = {
                "email": user.email,
                "username": user.username,
                "source_url": source_url or "Direct",
                "login_time": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "user_id": user.id
            }

            DjangoTelegram.send_success("✅ Successful OTP Login", verification_data)
            logger.info(f"OTP verification telegram notification sent for {user.email}")

    # === SECURITY NOTIFICATIONS ===

    @staticmethod
    def send_security_alert(user, alert_type, details, send_email=True, send_telegram=True):
        """Send security alert notification"""
        if send_email:
            AccountNotifications._send_email(
                user=user,
                subject=f"Security Alert: {alert_type} ⚠️",
                main_text="A security alert has been triggered for your account.",
                main_html_content=f'<p style="font-size: 1.5em; font-weight: bold; color: #dc3545;">{alert_type}</p>',
                secondary_text=f"Details: {details}\nIf this wasn't you, please contact support immediately.",
                button_text="Review Account",
            )
            logger.info(f"Security alert email sent to {user.email}")

        if send_telegram:
            alert_data = {
                "user": user.email,
                "alert_type": alert_type,
                "details": details,
                "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "user_id": user.id
            }

            DjangoTelegram.send_warning(f"🚨 Security Alert: {alert_type}", alert_data)
            logger.info(f"Security alert telegram notification sent for {user.email}")

    @staticmethod
    def send_failed_otp_attempt(identifier, ip_address=None, reason="Invalid OTP", send_telegram=True):
        """Send notification about failed OTP attempt"""
        if send_telegram:
            details = {
                "identifier": identifier,
                "reason": reason,
                "ip_address": ip_address or "Unknown",
                "attempt_time": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            }

            DjangoTelegram.send_warning("❌ Failed OTP Attempt 📧", details)
            logger.info(f"Failed OTP attempt telegram notification sent for {identifier}")

    @staticmethod
    def send_suspicious_activity(user, activity_type, details, send_email=True, send_telegram=True):
        """Send suspicious activity notification"""
        if send_email:
            AccountNotifications._send_email(
                user=user,
                subject=f"Security Alert: Suspicious Activity: {activity_type} ⚠️",
                main_text="A security alert has been triggered for your account.",
                main_html_content=f'<p style="font-size: 1.5em; font-weight: bold; color: #dc3545;">Suspicious Activity: {activity_type}</p>',
                secondary_text=f"Details: We detected suspicious activity on your account: {details.get('description', 'Unknown activity')}\nIf this wasn't you, please contact support immediately.",
                button_text="Review Account",
            )
            logger.info(f"Suspicious activity email sent to {user.email}")

        if send_telegram:
            alert_data = {
                "user": user.email,
                "activity_type": activity_type,
                "details": details,
                "timestamp": details.get("timestamp", timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC")),
                "ip_address": details.get("ip_address", "Unknown"),
                "user_agent": details.get("user_agent", "Unknown"),
                "requires_attention": True
            }

            DjangoTelegram.send_error(f"🚨 Suspicious Activity: {activity_type}", alert_data)
            logger.info(f"Suspicious activity telegram notification sent for {user.email}")

    # === ADMIN NOTIFICATIONS ===

    @staticmethod
    def send_admin_user_created(user, created_by=None, send_telegram=True):
        """Send notification when admin creates user"""
        if send_telegram:
            data = {
                "user": user.email,
                "username": user.username,
                "created_by": created_by.email if created_by else "System",
                "is_active": user.is_active,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
                "date_created": user.date_joined.strftime("%Y-%m-%d %H:%M:%S UTC")
            }

            DjangoTelegram.send_info("👨‍💼 Admin Created User", data)
            logger.info(f"Admin user creation telegram notification sent for {user.email}")

    @staticmethod
    def send_bulk_operation_notification(operation_type, count, details=None, send_telegram=True):
        """Send notification about bulk operations"""
        if send_telegram:
            data = {
                "operation": operation_type,
                "count": count,
                "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            }

            if details:
                data.update(details)

            DjangoTelegram.send_info(f"📊 Bulk Operation: {operation_type}", data)
            logger.info(f"Bulk operation telegram notification sent: {operation_type}")
