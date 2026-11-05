"""
User Account Notification System
Centralized email and telegram notifications for user account events
"""
import logging

from django.utils import timezone
from django.utils.translation import gettext, gettext_noop as _, override

from django_cfg.apps.system.mailer.templatetags.email_content import fill_placeholders
from django_cfg.core.site import Site, site_for
from django_cfg.modules.django_email import DjangoEmailService
from django_cfg.modules.django_email.service import text_direction
from django_cfg.modules.django_telegram import DjangoTelegram

logger = logging.getLogger(__name__)


def _site(site, user=None) -> Site:
    """The site a letter speaks for.

    ``site`` is a ``Site``, a site key (what a job captured), or None: then the
    user's own site (their first registration source), then the default site.
    Read per call, never bound at import: a process that later registers another
    config must not keep mailing the first one's name.
    """
    if isinstance(site, Site):
        return site
    return site_for(key=site, user=user)


def _locale(user, site: Site) -> str:
    """The user's language, else the site's locale."""
    from ..services.welcome import resolve_locale

    return resolve_locale(user, site=site)


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


def _subject(
    msgid: str, copy: dict, locale: str, params: dict, ensure: str = "", use_stored: bool = True,
) -> str:
    """A letter's subject, in the reader's language.

    A stored ``EmailContent`` subject wins; otherwise ``msgid`` goes through
    gettext (English when the project ships no catalog), with ``params`` filled
    in. ``ensure`` is text the subject must carry (the OTP code): appended if the
    stored copy left it out, because the recipient reads it from the preview.
    ``use_stored=False`` ignores a stored subject: for a letter whose subject must
    stay constant (the OTP code), so a stale stored row cannot bring back a
    changing one.
    """
    stored = (copy or {}).get("subject") if use_stored else None
    if stored:
        subject = fill_placeholders(stored, params)
    else:
        with override(locale):
            subject = gettext(msgid) % params
    if ensure and ensure not in subject:
        subject = f"{subject}: {ensure}"
    return subject


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
        # Optional: a letter whose whole content is a code has nothing to link
        # to, and the templates guard on both being set.
        button_text: str = None,
        button_url: str = None,
        template_name: str = "emails/base_email",
        to_email: str = None,
        locale: str = None,
        extra_context: dict = None,
        text_only: bool = False,
        copy_key: str = None,
        site=None,
        subject_params: dict = None,
        subject_ensure: str = "",
        use_stored_subject: bool = True,
    ):
        """Private method for sending templated emails.

        ``subject`` is the English message id, with ``%(project_name)s`` and any
        ``subject_params`` placeholders; it is translated and filled in here, or
        replaced by the stored per-locale subject (see ``_subject``).
        ``site`` is a ``Site``, a site key or None (the user's own site).

        ``copy_key`` names the *letter*; ``template_name`` names the *layout*.
        Keying copy off the template alone makes every letter sharing a layout
        share one row, so copy written for one comes back verbatim in another.
        A caller passing no ``copy_key`` still resolves off the template name.
        """
        email_service = DjangoEmailService()
        site = _site(site, user)
        locale = locale or _locale(user, site)
        copy = _resolve_copy(copy_key or template_name, locale)
        subject = _subject(
            subject, copy, locale, {**site.as_context(), **(subject_params or {})}, subject_ensure,
            use_stored_subject,
        )

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
            # Keyed off the letter, falling back to the template for callers that
            # name no letter of their own.
            "copy": copy,
        }
        if extra_context:
            context.update(extra_context)

        email_service.send_template(
            subject=subject,
            template_name=template_name,
            context=context,
            recipient_list=[to_email or user.email],
            locale=locale,
            text_only=text_only,
            site=site,
        )

    # === EMAIL NOTIFICATIONS ===

    @staticmethod
    def send_welcome_email(
        user, locale=None, send_email=True, send_telegram=True, text_only=True, site=None
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
            site = _site(site, user)
            AccountNotifications._send_email(
                user=user,
                site=site,
                subject=_("Welcome to %(project_name)s"),
                main_text=f"Welcome {user.username}! Your account has been successfully created.",
                main_html_content=f'<p style="font-size: 1.5em; font-weight: bold; color: #28a745;">Welcome {user.username}!</p>',
                secondary_text="You can now access all our services and start exploring our API.",
                button_text=f"Go to {site.name}",
                button_url=site.site_url,
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
    def send_profile_update_notification(
        user, changes, send_email=True, send_telegram=True, site=None, email_changes=None, email_to=None
    ):
        """Send profile update notification.

        ``changes`` is what Telegram reports. The letter names ``email_changes``
        (default: ``changes``) and goes to ``email_to`` (default: the user's
        address), so a changed address can warn the one it replaced.
        """
        if not changes:
            return

        change_text = ", ".join(changes)
        email_text = ", ".join(email_changes or changes)

        if send_email:
            AccountNotifications._send_email(
                user=user,
                site=site,
                subject=_("Security Alert: Profile Updated ⚠️"),
                copy_key="profile_updated",
                main_text="A security alert has been triggered for your account.",
                main_html_content='<p style="font-size: 1.5em; font-weight: bold; color: #dc3545;">Profile Updated</p>',
                secondary_text=f"Details: Your {email_text} has been updated. If this wasn't you, please contact support immediately.",
                button_text="Review Account",
                to_email=email_to,
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
    def send_account_status_change(user, status_type, reason=None, send_email=True, send_telegram=True, site=None):
        """Send account status change notification (activated/deactivated)"""
        if send_email:
            if status_type == "activated":
                site = _site(site, user)
                AccountNotifications._send_email(
                    user=user,
                    site=site,
                    subject=_("Account Activated - %(project_name)s ✅"),
                    copy_key="account_activated",
                    main_text="Your account has been activated and is now ready to use!",
                    main_html_content='<p style="font-size: 1.5em; font-weight: bold; color: #28a745;">Account Activated!</p>',
                    secondary_text="You now have full access to all our services and features.",
                    button_text="Access Private",
                    button_url=site.url("/private"),
                )
                logger.info(f"Account activation email sent to {user.email}")

            elif status_type == "deactivated":
                AccountNotifications._send_email(
                    user=user,
                    site=site,
                    subject=_("Account Status Update - %(project_name)s ⚠️"),
                    copy_key="account_deactivated",
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
    def send_login_notification(user, ip_address=None, send_email=False, send_telegram=True, site=None):
        """Send login notification (usually only telegram for security monitoring)"""
        if send_email:
            login_time = timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            ip_text = f" from IP address {ip_address}" if ip_address else ""
            AccountNotifications._send_email(
                user=user,
                site=site,
                subject=_("Login Notification - %(project_name)s 🔐"),
                copy_key="login_notification",
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
    def send_otp_notification(
        user, otp_code, is_new_user=False, source_url=None, send_email=True, send_telegram=True, site=None
    ):
        """Send OTP notification via email"""
        if send_email:
            from ..models.auth import OTPSecret

            AccountNotifications._send_email(
                user=user,
                site=site,
                # The subject is constant: a code in it made every letter a new
                # Gmail thread. The code leads the body instead (the hidden
                # preheader in otp_email.html), which is what the inbox preview
                # shows. A stored per-locale subject is ignored for the same reason.
                subject=_("🔐 Your login code"),
                use_stored_subject=False,
                copy_key="otp_code",
                main_text="Use the code below to sign in:",
                main_html_content="",
                secondary_text=f"This code expires in {OTPSecret.EXPIRY_MINUTES} minutes.",
                # No magic link: it carried the code in the URL, leaking it to
                # referrers, history and link-preview bots that would spend it
                # first. A link needs a host allowlist before it can come back.
                button_text=None,
                button_url=None,
                # Own layout: `base_email` is built around a CTA button this
                # letter does not have.
                template_name="emails/otp_email",
                extra_context={
                    "otp_code": otp_code,
                    "expires_minutes": OTPSecret.EXPIRY_MINUTES,
                },
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
    def send_security_alert(user, alert_type, details, send_email=True, send_telegram=True, site=None):
        """Send security alert notification"""
        if send_email:
            AccountNotifications._send_email(
                user=user,
                site=site,
                subject=_("Security Alert: %(alert_type)s ⚠️"),
                subject_params={"alert_type": alert_type},
                copy_key="security_alert",
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
    def send_suspicious_activity(user, activity_type, details, send_email=True, send_telegram=True, site=None):
        """Send suspicious activity notification"""
        if send_email:
            AccountNotifications._send_email(
                user=user,
                site=site,
                subject=_("Security Alert: Suspicious Activity: %(activity_type)s ⚠️"),
                subject_params={"activity_type": activity_type},
                copy_key="suspicious_activity",
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
